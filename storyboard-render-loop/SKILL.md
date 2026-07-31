---
name: storyboard-render-loop
description: >-
  End-to-end agentic pipeline that turns a raw novel excerpt into rendered
  storyboard frames (分镜图) and self-corrects them. Use this whenever the user
  wants to go from novel/story text all the way to actual generated storyboard
  IMAGES via a ComfyUI Z-Image Turbo endpoint — not just prompts. Triggers on
  requests like "把这段小说生成分镜图", "render the storyboard", "generate
  storyboard images and check them", "novel to storyboard images", "run the
  screenplay + storyboard + image pipeline", "call ComfyUI to make the frames
  and fix the bad ones", or any ask that combines screenplay/storyboard
  generation with actually rendering and visually QA-ing the images in a loop.
  This skill orchestrates the screenplay-writer and storyboard-prompt skills,
  calls the ComfyUI API to render each shot, uses a vision subagent to inspect
  every frame one by one, and revises prompts and retries until each frame is
  good or the retry limit is hit. Use it even when the user only says "generate
  the images for this" if a novel/script/storyboard is in play.
---

# Storyboard render loop (novel → screenplay → storyboard → rendered frames)

This skill is an **orchestrator**. It chains two upstream skills and a ComfyUI
image backend into one closed feedback loop:

```
novel text
   │  (screenplay-writer skill)
   ▼
剧本 / screenplay  ──(storyboard-prompt skill)──▶  分镜表 + Z-Image prompts + anchors
                                                        │
                          ┌─────────────────────────────┘
                          ▼   serial, one shot at a time
                render shot ──▶ vision QA ──▶ pass? ── yes ─▶ mark solid
                     ▲               │
                     └── revise ◀── no (attempts < limit)
                                     │
                                  limit hit ─▶ mark failed
```

The point of the loop is that a distilled text-to-image model will get *some*
frames wrong (missing subject, artifacts, wrong framing). Instead of dumping all
images on the user, the agent inspects each frame itself, diagnoses the specific
defect, rewrites just that prompt using Z-Image Turbo tactics, and retries — the
same thing a human operator would do, but automatically.

## Prerequisites

Confirm these before starting; if something is missing, say so rather than
guessing:

1. **Upstream skills present.** This skill invokes the `screenplay-writer` and
   `storyboard-prompt` skills. They live alongside this one. Read their SKILL.md
   files and follow them for stages 1–2 — do not reinvent screenplay/storyboard
   conventions here.
2. **ComfyUI endpoint.** A ComfyUI server with Z-Image Turbo runs on a box
   reachable on the LAN (often a separate GPU machine, not the agent's machine).
   Set `COMFYUI_HOST`, e.g. `http://192.168.1.50:8188`. See
   `references/comfyui-api.md`. Verify reachability first with a `--dry-run` or
   `curl <host>/system_stats`.
3. **Vision-capable inspection.** The QA step needs an agent that can view
   images. Spawn a subagent per frame using `agents/qa-inspect.md`.
4. **Output dir.** Pick a run directory, e.g. `renders/<slug>/`, for images and
   the state manifest.

## Inputs to gather

Ask only for what's missing; infer sensible defaults otherwise:

- The **novel excerpt** (raw text) — required.
- **集数/场次 scope** — which part to storyboard (default: the provided excerpt
  as one 场次/scene, or let screenplay-writer segment it).
- **Retry limit** per shot — default **3**.
- **Aspect/size** — default 1280×720 for cinematic shots; 1024×1024 for
  portraits/close-ups. storyboard-prompt already suggests per-shot params.
- **COMFYUI_HOST** — from env/.env or ask.

## Stage 1 — Novel → screenplay

Follow the `screenplay-writer` skill on the novel excerpt to produce the 剧本
(集数-场次 headings, ▲ action, 台词, VO/OS). Keep it — it is the ground truth for
what each scene contains.

## Stage 2 — Screenplay → storyboard + Z-Image prompts

Follow the `storyboard-prompt` skill (Z-Image Turbo mode) on the screenplay to
produce, per shot: 镜号, 景别, 运镜, 机位, 画面描述, 对白, **用到的锚点**, the
full **Z-Image Turbo positive prompt**, and 建议参数 (steps/cfg/size/seed). Also
capture the scene-level **画风 (style phrase)** and the **锚点表 (anchors)** —
these are what keep characters/props consistent across frames and what the QA
step checks against.

## Stage 3 — Build the render-state manifest

Create `renders/<slug>/render-state.json`: one record per shot. This is the
loop's memory — update it after every attempt so the run is resumable and the
final report is trivial to produce.

```json
{
  "slug": "duanhun-ya",
  "host": "http://192.168.1.50:8188",
  "style_phrase": "国风水墨与写实结合、冷色调、电影感",
  "anchors": {
    "林越": "清瘦的约十六岁外门弟子，粗布长袍，左眉有一道小疤",
    "断魂崖": "陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾"
  },
  "retry_limit": 3,
  "shots": [
    {
      "id": "2-3-01",
      "景别": "全景", "机位": "侧面低机位",
      "画面描述": "狂风扫过断崖，林越被赵天骄一掌击飞…",
      "用到的锚点": ["林越", "赵天骄", "断魂崖"],
      "params": {"steps": 10, "cfg": 1.0, "width": 1280, "height": 720, "seed": 12345},
      "prompt": "电影感全景，侧面低机位…画面干净，无文字、无水印…",
      "attempts": [],
      "status": "pending",
      "image_path": null
    }
  ]
}
```

`status` ∈ `pending | solid | failed`. Each entry in `attempts` records
`{n, seed, prompt, image_path, verdict, reasons, anchor_drift}`.

## Stage 4 — The render + QA loop (SERIAL, one shot at a time)

Process shots **strictly one at a time, in order**. Do not batch-render then
batch-review — serial processing is what lets a lesson learned on an early frame
(e.g. an anchor that keeps drifting, a seed that composes badly) inform the
prompt for the next one, and it keeps the ComfyUI box from thrashing. Within a
shot, loop until pass or limit:

For each shot `s`:

1. **Render.** Run the client (fix the seed so revisions are comparable):

   ```
   python scripts/comfy_zimage.py \
     --host "$COMFYUI_HOST" \
     --prompt "<s.prompt>" \
     --seed <s.params.seed> --steps <s.params.steps> --cfg <s.params.cfg> \
     --width <s.params.width> --height <s.params.height> \
     --filename-prefix "shot_<s.id>" \
     --out "renders/<slug>/<s.id>_a<attempt>.png"
   ```

   Parse the JSON result line. On `status:"error"`, treat it as a failed attempt
   (record the error); if it's an endpoint/config error (unreachable, wrong
   format), STOP the whole run and tell the user — retrying won't help.

2. **Inspect.** Spawn a vision subagent with `agents/qa-inspect.md`, passing the
   image path, `s.id`, `画面描述`, the relevant `锚点` (verbatim), `景别/机位/运镜`,
   the exact prompt used, and the attempt number. It returns a strict
   `VERDICT: pass|fail` block with `REASONS`, `ANCHOR_DRIFT`, `REVISED_PROMPT`,
   `SEED_ADVICE`.

3. **Decide.**
   - **pass** → set `status:"solid"`, `image_path` to this render, record the
     attempt, move to the next shot.
   - **fail** and `attempts < retry_limit` → apply the QA subagent's
     `REVISED_PROMPT` (or, if you disagree, craft a better fix using
     `references/z-image-turbo.md` tactics — reinforce the missed element, repeat
     the anchor verbatim, tighten the cleanliness clause). Follow `SEED_ADVICE`:
     keep the seed for a targeted wording fix, pick a new seed for a
     composition-level miss. Re-render (back to step 1).
   - **fail** and `attempts == retry_limit` → set `status:"failed"`, keep the
     best attempt's image, record why. Do NOT let one stubborn frame stall the
     whole run.

4. **Persist.** Update `render-state.json` after every attempt.

### Why fix in the positive prompt only

Z-Image Turbo runs at CFG≈0/1 and **ignores negative prompts**, so "remove X"
must be phrased as positive constraints (`画面干净，无文字、无水印、无多余人物，
正确的手部与肢体结构`). The QA subagent is told this; when you revise, keep
exclusions in the positive prompt too. See `references/z-image-turbo.md`.

## Stage 5 — Final report

When all shots are `solid` or `failed`, summarize for the user:

- A table: 镜号 | status | attempts | image_path | one-line note.
- Call out any `failed` shots with the QA reasons and suggest next moves
  (different seed range, simplify the shot, split into two shots, or hand-edit).
- Point to `render-state.json` and the image directory.
- Offer first/last-frame prompts (already in the storyboard) if the user wants
  to take solid frames into image-to-video next.

Keep the report concise and skimmable. Show the images inline if the environment
supports it.

## Operating notes

- **Serial, not parallel.** One shot fully done before the next.
- **Fixed seed while tuning.** Only change the seed when QA says the composition
  itself is wrong; otherwise keep it so prompt edits are the only variable.
- **Anchors are law.** Never paraphrase an anchor between shots — drift is the
  #1 cause of inconsistent characters. If QA reports drift, re-pin the exact
  anchor phrase in the prompt.
- **Fail loudly on infra errors.** A rendered-but-wrong image is a loop problem;
  an unreachable endpoint or bad workflow is a stop-and-tell-the-user problem.
- **Resumability.** Because state lives in `render-state.json`, a run can be
  re-entered: skip `solid` shots, retry `pending`/`failed` as directed.

## Bundled resources

- `scripts/comfy_zimage.py` — stdlib-only ComfyUI client: patches an API-format
  workflow, submits, polls, downloads. Robust node-finding; `--dry-run` to
  validate targeting. See its `--help`.
- `scripts/zimage_workflow.api.json` — default API workflow for the standard
  Z-Image Turbo setup. Override with `--workflow` if your graph differs.
- `agents/qa-inspect.md` — the per-frame vision-QA subagent prompt.
- `references/comfyui-api.md` — endpoint details, workflow export, params,
  troubleshooting.
- `references/z-image-turbo.md` — (in the storyboard-prompt skill) the prompt
  wording playbook the revision step draws on.
