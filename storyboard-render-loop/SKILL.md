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
produce, per shot: 镜号, 景别, 运镜, 机位, 画面描述(首→尾), 对白, **用到的锚点**,
and — the key outputs this loop renders — a **首帧 (start) prompt** and a
**尾帧 (end) prompt** (two full Z-Image positive prompts sharing one seed), each
with 建议参数 (steps/cfg/size/seed), plus an **LTX-2.3 FLF2V video prompt** that
animates 首帧→尾帧 and **keeps the shot's 台词 and VO/旁白** (LTX-2.3 generates
synchronized audio incl. dialogue). Also capture the scene-level **画风 (style
phrase)** and the **锚点表 (anchors)** — these keep characters/props consistent
across frames and are what the QA step checks against.

Each shot therefore has **two frames to render** (首帧 and 尾帧). The video prompt
is carried through but **not rendered** — video generation is out of scope for
this loop; it is stored, ready for LTX-2.3's first-last-frame workflow using the
two solid frames as anchors.

## Stage 3 — Build the render-state manifest

Create `renders/<slug>/render-state.json`: one record per shot, with a `first`
and `last` frame sub-record. This is the loop's memory — update it after every
attempt so the run is resumable and the final report is trivial to produce.

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
      "id": "2-3-06",
      "景别": "全景", "机位": "侧面平视",
      "画面描述": "赵天骄抬腿 → 踹中林越，林越越过崖线坠出",
      "用到的锚点": ["林越", "赵天骄", "断魂崖", "残破玉简"],
      "params": {"steps": 10, "cfg": 1.0, "width": 1280, "height": 720, "seed": 4477},
      "video_prompt": "全景侧面平视，镜头随白衣青年抬腿而缓慢侧移…赵天骄冷笑着说：“一个废物，也配觊觎宗门功法？”…林越（画外音，压抑）：“我不甘心……”…约4秒，前段蓄力、后段失重。画面无字幕、无水印。",
      "frames": {
        "first": {
          "prompt": "电影感全景侧面平视…冷笑抬腿正欲踹出…画面干净，无文字…",
          "attempts": [], "status": "pending", "image_path": null
        },
        "last": {
          "prompt": "电影感全景侧面平视…一脚已踹中…越过崖线坠出…画面干净，无文字…",
          "attempts": [], "status": "pending", "image_path": null
        }
      },
      "status": "pending"
    }
  ]
}
```

Frame `status` ∈ `pending | solid | failed`. Each entry in a frame's `attempts`
records `{n, seed, prompt, image_path, verdict, reasons, anchor_drift}`. A shot's
top-level `status` is `solid` only when **both** frames are `solid`; `failed` if
either frame ends `failed`. 首帧 and 尾帧 share the same seed (from `params.seed`)
so the pair stays coherent.

## Stage 4 — The render + QA loop (SERIAL, one frame at a time)

Process shots **strictly one at a time, in order**, and within a shot render the
**首帧 then the 尾帧**. Do not batch-render then batch-review — serial processing
is what lets a lesson learned on an early frame (e.g. an anchor that keeps
drifting, a seed that composes badly) inform the next frame/shot, and it keeps
the ComfyUI box from thrashing.

For each shot `s`, for each frame `f` in (`first`, `last`), loop until pass or limit:

1. **Render.** Run the client (both frames use `s.params.seed` so the pair is
   comparable and coherent):

   ```
   python scripts/comfy_zimage.py \
     --host "$COMFYUI_HOST" \
     --prompt "<s.frames[f].prompt>" \
     --seed <s.params.seed> --steps <s.params.steps> --cfg <s.params.cfg> \
     --width <s.params.width> --height <s.params.height> \
     --filename-prefix "shot_<s.id>_<f>" \
     --out "renders/<slug>/<s.id>_<f>_a<attempt>.png"
   ```

   The client strips any stray `建议参数` / 运镜 line from the prompt, so passing
   a slightly-dirty prompt is safe — but pass only the frame's image prompt, never
   the motion prompt. Parse the JSON result line. On `status:"error"`, treat it as
   a failed attempt (record the error); if it's an endpoint/config error
   (unreachable, wrong format), STOP the whole run and tell the user — retrying
   won't help.

2. **Inspect.** Spawn a vision subagent with `agents/qa-inspect.md`, passing the
   image path, `s.id` + which frame (`first`/`last`), the frame's expected
   moment-in-time from `画面描述` (首 or 尾 phase), the relevant `锚点` (verbatim),
   `景别/机位/运镜`, the exact prompt used, and the attempt number. It returns a
   strict `VERDICT: pass|fail` block with `REASONS`, `ANCHOR_DRIFT`,
   `REVISED_PROMPT`, `SEED_ADVICE`.

   When inspecting the **尾帧**, also check it is **consistent with the already-
   solid 首帧** (same character look/anchors, same environment/lighting/style) and
   differs only in the action phase — a 尾帧 that drifts from its 首帧 fails, since
   the pair must interpolate as one shot.

3. **Decide.**
   - **pass** → set the frame's `status:"solid"`, `image_path` to this render,
     record the attempt, move to the next frame/shot.
   - **fail** and `attempts < retry_limit` → apply the QA subagent's
     `REVISED_PROMPT` (or, if you disagree, craft a better fix using
     `references/z-image-turbo.md` tactics — reinforce the missed element, repeat
     the anchor verbatim, tighten the cleanliness clause). Follow `SEED_ADVICE`:
     keep the seed for a targeted wording fix, pick a new seed for a
     composition-level miss (if you re-seed the 尾帧, prefer re-seeding both frames
     together so the pair stays coherent). Re-render (back to step 1).
   - **fail** and `attempts == retry_limit` → set the frame's `status:"failed"`,
     keep the best attempt's image, record why. Do NOT let one stubborn frame
     stall the whole run.

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
- When both frames of a shot are solid, note that the shot is ready for LTX-2.3
  FLF2V: 首帧 + 尾帧 as the start/end images and the stored `video_prompt`
  (which carries the 台词/VO). Video generation itself stays out of scope here.

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
- `references/z-image-turbo.md` — the Z-Image prompt wording playbook the
  revision step draws on.
- `references/ltx2-video.md` — the LTX-2.3 FLF2V video-prompt playbook (dialogue/
  VO/audio syntax) for the carried-through `video_prompt`.
