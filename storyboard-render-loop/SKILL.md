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
  each frame, and revises prompts until it passes or reaches the retry limit.
  Use it when "generate the images" refers to a novel, script, or storyboard.
---

# Storyboard render loop (novel → screenplay → storyboard → rendered frames)

This skill is an **orchestrator**. It chains two upstream skills and a ComfyUI
image backend into one closed feedback loop:

```
novel text
   │  (screenplay-writer skill)
   ▼
剧本 / screenplay  ──(storyboard-prompt skill)──▶  分镜表 + H3端点帧(K0/K1) + H3提示 + anchors
                                                        │
                          ┌─────────────────────────────┘
                          ▼   serial, one keyframe at a time
         render keyframe Ki ──▶ vision QA ──▶ pass? ── yes ─▶ mark solid
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

Follow the `storyboard-prompt` skill (Z-Image Turbo + MiniMax-H3 mode) on the
screenplay. For the default FL2VA path, each shot supplies **K0 / Picture 1** and
**K1 / Picture 2**, complete Z-Image prompts for the exact opening and ending
frames of one 4–15 second H3 shot, plus one H3 audiovisual prompt describing the
continuous action path, stable speakers, verbatim dialogue/VO, soundscape, and
music. Also capture the scene-level **画风**, **锚点表**, speaker registry, H3 mode,
duration, and request parameters.

A normal FL2VA shot therefore has **two endpoint frames and one H3 request**.
Optional intermediate storyboard images are planning aids, not H3 API inputs.
Ref2VA shots carry an ordered reference manifest and must not mix reference roles
with first/last-frame roles. Video generation remains out of scope for this loop.

## Stage 3 — Build the render-state manifest

Create `renders/<slug>/render-state.json`: one record per shot, carrying a
`keyframes` list and an `h3_generation` object with mode, duration, endpoint or
reference mapping, and the complete audiovisual prompt. This is the loop's memory — update it after
every attempt so the run is resumable and the final report is trivial to produce.

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
      "id": "2-3-05",
      "景别": "全景", "机位": "侧面平视",
      "动作路径": "K0 抬腿蓄力 → 踹实、少年双脚离地 → K1 越崖坠出",
      "duration": 6,
      "h3_mode": "fl2va",
      "用到的锚点": ["林越", "赵天骄", "断魂崖", "残破玉简"],
      "seed": 4477,
      "keyframes": [
        {
          "id": "K0",
          "prompt": "电影感中近景侧面平视…冷笑抬腿正欲踹出…画面干净，无文字…",
          "params": {"steps": 10, "cfg": 1.0, "width": 1280, "height": 720},
          "attempts": [], "status": "pending", "image_path": null
        },
        {
          "id": "K1",
          "prompt": "电影感远景高角度俯视…越过崖线坠出、空中失衡旋转…画面干净，无文字…",
          "params": {"steps": 10, "cfg": 1.0, "width": 1280, "height": 720},
          "attempts": [], "status": "pending", "image_path": null
        }
      ],
      "h3_generation": {
        "model": "MiniMax-H3",
        "mode": "fl2va",
        "duration": 6,
        "resolution": "2K",
        "ratio": "adaptive",
        "first_frame": "K0",
        "last_frame": "K1",
        "prompt": "How the reference pictures align with the target video — Picture 1..."
      },
      "status": "pending"
    }
  ]
}
```

Keyframe `status` ∈ `pending | solid | failed`. Each entry in a keyframe's
`attempts` records `{n, seed, prompt, image_path, verdict, reasons, anchor_drift}`.
A shot's top-level `status` is `solid` only when **all** keyframes are `solid`;
`failed` if any keyframe ends `failed`. Endpoint frames normally share the shot's
`seed` as a Z-Image continuity aid. `h3_generation.first_frame` and `last_frame`
must resolve to solid images, and duration must be an integer from 4 through 15.

## Stage 4 — The render + QA loop (SERIAL, one keyframe at a time)

Process shots **strictly one at a time, in order**, and within a FL2VA shot render
**K0 then K1** (plus any explicitly requested planning frames). Do not batch-render then batch-review — serial
processing is what lets a lesson learned on an early keyframe (e.g. an anchor that
keeps drifting, a seed that composes badly) inform the next keyframe/shot, and it
keeps the ComfyUI box from thrashing.

For each shot `s`, for each keyframe `k` in `s.keyframes` (in order), loop until
pass or limit:

1. **Render.** Run the client (every keyframe uses `s.seed` so the chain is
   coherent):

   ```
   python scripts/comfy_zimage.py \
     --host "$COMFYUI_HOST" \
     --prompt "<k.prompt>" \
     --seed <s.seed> --steps <k.params.steps> --cfg <k.params.cfg> \
     --width <k.params.width> --height <k.params.height> \
     --filename-prefix "shot_<s.id>_<k.id>" \
     --out "renders/<slug>/<s.id>_<k.id>_a<attempt>.png"
   ```

   The client strips any stray `参数` / 运镜 line from the prompt, so passing a
   slightly-dirty prompt is safe — but pass only the keyframe's image prompt, never
   a video/motion prompt. Parse the JSON result line. On `status:"error"`, treat it
   as a failed attempt (record the error); if it's an endpoint/config error
   (unreachable, wrong format), STOP the whole run and tell the user — retrying
   won't help.

2. **Inspect.** Spawn a vision subagent with `agents/qa-inspect.md`, passing the
   image path, `s.id` + which keyframe (`K0`/`K1`/…), the keyframe's expected
   moment-in-time from `关键帧节拍`, the relevant `锚点` (verbatim), `景别/机位/运镜`,
   the exact prompt used, and the attempt number. It returns a strict
   `VERDICT: pass|fail` block with `REASONS`, `ANCHOR_DRIFT`, `REVISED_PROMPT`,
   `SEED_ADVICE`.

   For K1, also check it is **consistent with K0** in character identity, location,
   aspect ratio, lighting, and style, and that the storyboard's action path can
   plausibly connect the endpoints within the declared 4–15 seconds. A deliberate
   action or composition change is expected; identity or scene drift is not.

3. **Decide.**
   - **pass** → set the keyframe's `status:"solid"`, `image_path` to this render,
     record the attempt, move to the next keyframe/shot.
   - **fail** and `attempts < retry_limit` → apply the QA subagent's
     `REVISED_PROMPT` (or, if you disagree, craft a better fix using
     `references/z-image-turbo.md` tactics — reinforce the missed element, repeat
     the anchor verbatim, tighten the cleanliness clause). Follow `SEED_ADVICE`:
     keep the seed for a targeted wording fix; a composition-level miss on one
     keyframe usually means re-seeding the **whole chain** (all keyframes) together
     so they stay coherent, then re-render from K0. Re-render (back to step 1).
   - **fail** and `attempts == retry_limit` → set the keyframe's `status:"failed"`,
     keep the best attempt's image, record why. Do NOT let one stubborn keyframe
     stall the whole run.
   - **endpoint path implausible** → if K0 and K1 require a location change, unrelated
     camera setup, or several disconnected actions, rewording will not help. Split
     the beat into separate 4–15 second H3 shots and regenerate each shot's endpoint
     frames and H3 prompt.
   - **overloaded frame** → if failures recur because a keyframe has too many
     subjects/props/actions to render reliably (elements keep dropping or swapping,
     not a wording slip), rewording won't help. Flag the shot as needing a **split**
     (per `storyboard-prompt` Pass 1's complexity budget): break it into
     establishing → 中景 → 近景 or sub-shots `<id>a/<id>b`, regenerate their chains,
     and render those instead. Record the split in the manifest and tell the user.

4. **Persist.** Update `render-state.json` after every attempt.

### Why fix in the positive prompt only

Z-Image Turbo runs at CFG≈0/1 and **ignores negative prompts**, so "remove X"
must be phrased as positive constraints (`画面干净，无文字、无水印、无多余人物，
正确的手部与肢体结构`). The QA subagent is told this; when you revise, keep
exclusions in the positive prompt too. See `references/z-image-turbo.md`.

## Stage 5 — Final report

When all shots are `solid` or `failed`, summarize for the user:

- A table: 镜号 | status | keyframes solid/total | attempts | image paths | one-line note.
- Call out any `failed` keyframes with the QA reasons and suggest next moves
  (different seed range, simplify the shot, insert/split keyframes, or hand-edit).
- Point to `render-state.json` and the image directory.
- When both endpoint frames are solid, note that the shot is ready for MiniMax-H3
  FL2VA using K0 as `first_frame`, K1 as `last_frame`, and the complete H3 prompt.
  For Ref2VA, report that its ordered reference manifest and six-section prompt are
  ready. Video generation itself stays out of scope here.

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
- `references/minimax-h3-video.md` — official-guide-derived H3 Base/Ref2VA prompt
  contracts, dialogue/VO syntax, audio fields, and request validation.
