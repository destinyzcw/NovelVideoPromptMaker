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
剧本 / screenplay  ──(storyboard-prompt skill)──▶  分镜表 + 关键帧链(K0…Kn) + 逐段视频提示 + anchors
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

Follow the `storyboard-prompt` skill (Z-Image Turbo mode) on the screenplay to
produce, per shot: 镜号, 景别, 运镜, 机位, 关键帧节拍(K0→…→Kn), 对白, **用到的锚点**,
and — the key outputs this loop renders — a **keyframe chain** `K0 → K1 → … → Kn`
(每个 Ki 是一条完整的 Z-Image 正向提示词，整条链共享一个 seed；相邻两帧只在动作/
表情阶段不同，构成一个可被 FLF2V 平滑插值的小 delta)，外加**逐段视频提示**：每相邻
一对 `Ki→Ki+1` 一条 LTX-2.3 FLF2V 提示词，动画化该小段并**保留该段的 台词 与 VO/
旁白**（LTX-2.3 生成含对白的同步音频）。Also capture the scene-level **画风 (style
phrase)** and the **锚点表 (anchors)** — these keep characters/props consistent
across frames and are what the QA step checks against.

A shot therefore has **n+1 keyframes to render** (K0…Kn) and **n video segments**
(K0→K1, …, Kn-1→Kn). Simple/near-static shots stay 2 keyframes = 1 segment. The
video prompts are carried through but **not rendered** — video generation is out of
scope for this loop; they are stored, ready for LTX-2.3's FLF2V workflow using each
adjacent keyframe pair as the start/end anchors.

## Stage 3 — Build the render-state manifest

Create `renders/<slug>/render-state.json`: one record per shot, carrying a flat
`keyframes` list (the images to render, in order) and a `segments` list (the video
prompts joining adjacent keyframes). This is the loop's memory — update it after
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
      "景别": "中近景→远景", "机位": "侧面平视→高角度俯视",
      "关键帧节拍": "K0 抬腿蓄力 → K1 踹实、少年双脚离地 → K2 越崖坠出",
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
          "prompt": "电影感中近景侧面平视…一脚已踹中…双脚离地仍在崖线内…画面干净，无文字…",
          "params": {"steps": 10, "cfg": 1.0, "width": 1280, "height": 720},
          "attempts": [], "status": "pending", "image_path": null
        },
        {
          "id": "K2",
          "prompt": "电影感远景高角度俯视…越过崖线坠出、空中失衡旋转…画面干净，无文字…",
          "params": {"steps": 10, "cfg": 1.0, "width": 1280, "height": 720},
          "attempts": [], "status": "pending", "image_path": null
        }
      ],
      "segments": [
        {"from": "K0", "to": "K1", "video_prompt": "中近景侧面横移…赵天骄冷笑着说：“一个废物，也配觊觎宗门功法？”…约3秒，前段蓄力、后段猛烈命中。画面无字幕、无水印。"},
        {"from": "K1", "to": "K2", "video_prompt": "镜头从崖边向外跟摇下坠…林越（画外音，压抑）：“我不甘心……”…约4秒，前段越线失重、后段坠向冷雾。画面无字幕、无水印。"}
      ],
      "status": "pending"
    }
  ]
}
```

Keyframe `status` ∈ `pending | solid | failed`. Each entry in a keyframe's
`attempts` records `{n, seed, prompt, image_path, verdict, reasons, anchor_drift}`.
A shot's top-level `status` is `solid` only when **all** keyframes are `solid`;
`failed` if any keyframe ends `failed`. **All keyframes in a shot share the shot's
`seed`** so the chain stays coherent. Each `segments[i]` references two keyframe ids;
the shared boundary keyframe (e.g. K1) is rendered **once** and reused as the end of
one segment and the start of the next — never render or reword it twice.

## Stage 4 — The render + QA loop (SERIAL, one keyframe at a time)

Process shots **strictly one at a time, in order**, and within a shot render the
keyframes **K0, K1, … Kn in order**. Do not batch-render then batch-review — serial
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

   For every keyframe after K0, also check it is **consistent with the previous
   already-solid keyframe** (same character look/anchors, same environment/lighting/
   style) and that the change from the previous keyframe is a **small, FLF2V-
   interpolatable delta** — one continuous motion beat, not a big jump. A keyframe
   that drifts from its predecessor, or that is too far from it to interpolate,
   fails: adjacent frames must join as one seamless segment.

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
   - **delta too big** → if a keyframe keeps failing the adjacency check because the
     jump from the previous keyframe is too large to interpolate (not a wording
     slip), rewording won't help. **Insert an intermediate keyframe** between them
     (per `storyboard-prompt` Pass 2's delta budget), splitting that segment into
     two smaller beats; generate its prompt (same seed) and its two video prompts,
     add them to `keyframes`/`segments`, and render the new keyframe. Record the
     insertion in the manifest and tell the user.
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
- When all keyframes of a shot are solid, note that the shot is ready for LTX-2.3
  FLF2V: render each `segments[i]` as one short clip using keyframe `from` + `to`
  as the start/end images and its `video_prompt` (which carries the 台词/VO), then
  concatenate the clips in order (the shared boundary keyframe makes the joins
  seamless). Video generation itself stays out of scope here.

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
