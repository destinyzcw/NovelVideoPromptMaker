# NovelVideoPromptMaker

Agent **skills** for the story → screen pipeline: turn a story into a structured
screenplay (剧本), turn each scene into a shot list plus ready-to-use image prompts for
storyboard frames (分镜图), and — optionally — **render those frames on a ComfyUI
Z-Image Turbo endpoint and self-correct them in an agentic loop**. The first two skills
encode *workflow, reasoning discipline, and loop control* and stay backend-agnostic; the
third wires them to an actual image backend and adds a vision-QA retry loop.

The approach is distilled from the multi-agent prompt design of
[Stonewuu/ai-fusion-video](https://github.com/Stonewuu/ai-fusion-video) (融光), reframed as
standalone skills and stripped of that project's built-in image/video generation machinery.

## Skills

| Skill | Stage | Input | Output |
|-------|-------|-------|--------|
| [`screenplay-writer`](screenplay-writer/SKILL.md) | 1 — 剧本 | Story synopsis/outline, or existing prose | Markdown screenplay: episodes → scenes → dialogue |
| [`storyboard-prompt`](storyboard-prompt/SKILL.md) | 2 — 分镜图 prompt | A screenplay scene + visual assets | Shot-list table + a natural-language image prompt per shot |
| [`storyboard-render-loop`](storyboard-render-loop/SKILL.md) | 3 — render + QA | A novel excerpt (orchestrates 1+2) + a ComfyUI endpoint | Rendered storyboard PNGs, vision-QA'd and retried, plus a state manifest |

They chain: `screenplay-writer` output feeds `storyboard-prompt`; `storyboard-render-loop`
orchestrates both and then renders.

```
story / prose ──▶ screenplay-writer ──▶ 剧本 (scenes+dialogue)
                                            │
                                            ▼
                       storyboard-prompt ──▶ 分镜脚本 + 分镜图 prompts
                                            │
                                            ▼
                  storyboard-render-loop ──▶ ComfyUI Z-Image Turbo ──▶ frames ──▶ vision QA ──▶ revise/retry
```

### screenplay-writer (剧本)
- Two modes: **generate from outline** (invent scenes faithful to the synopsis) and
  **adapt existing prose** (restructure only what's written — never fabricate later events).
- Three-pass loop: story bible (characters/scenes/props) → episode plan (per-episode
  concept) → scenes & dialogue, processing **every** planned episode without skipping.
- Conventions: `集数-场次 地点 时间内外景` headings, `▲` action, `VO`/`OS`, `【】` camera
  cues, `角色名：台词` dialogue, and strict naming consistency.

### storyboard-prompt (分镜图 prompt)
- Establishes the visual bible first (a reusable **style phrase** + per-entity **anchor phrases**),
  deciding which appearance changes need a separate anchor vs. words.
- Shot design driven by drama: 正反打 for dialogue, 跟拍/手持 for action, 特写+慢推 for
  emotion; per shot picks 景别 / 时长 / 运镜 / 机位 / 画面描述 / 对白.
- Per shot it emits **two** Z-Image Turbo image prompts — a **首帧 (start)** and **尾帧 (end)**
  keyframe (identical except the action phase, sharing one seed) — plus an **LTX-2.3 FLF2V video
  prompt** that animates start→end and **keeps the scene's narration and dialogue** (LTX-2.3
  generates synchronized audio incl. speech; dialogue/VO go in the prompt with speaker + tone).
- Composes the image prompts for the default backend — **Z-Image Turbo (Tongyi-MAI) in ComfyUI**:
  long natural-language prompts, identity carried by verbatim anchor phrases (the base model is
  text-to-image with no reference-image input), exclusions baked into the positive prompt (negative
  prompts are ignored / CFG=0), lighting as its own clause, and suggested ComfyUI parameters —
  **without calling any model.** Reference playbooks are included for Z-Image Turbo, LTX-2.3 video,
  and other reference-capable image backends.

### storyboard-render-loop (novel → rendered frames)
- **Orchestrator** that runs the two skills above on a novel excerpt, then renders every shot
  on a **remote ComfyUI Z-Image Turbo** box over HTTP and self-corrects.
- **Serial, closed loop per shot**: render → a vision subagent inspects the frame against its
  画面描述 + anchors → pass, or revise the prompt (using Z-Image tactics) and retry until solid
  or the retry limit (default 3) is hit.
- Keeps a resumable `render-state.json` manifest (prompt, seed, attempts, verdict per shot),
  fails loudly on endpoint/config errors, and produces a final status report.
- Ships a **stdlib-only** ComfyUI client (`scripts/comfy_zimage.py`), a default API workflow
  (`scripts/zimage_workflow.api.json`), and a QA subagent prompt (`agents/qa-inspect.md`).
  The ComfyUI server runs on a separate GPU box on your LAN — set `COMFYUI_HOST`.

## Layout

```
NovelVideoPromptMaker/
├── README.md
├── screenplay-writer/
│   ├── SKILL.md
│   └── references/conventions.md          # deep conventions, edge cases, examples
├── storyboard-prompt/
│   ├── SKILL.md
│   └── references/
│       ├── z-image-turbo.md               # DEFAULT image backend: Z-Image Turbo in ComfyUI
│       ├── ltx2-video.md                  # DEFAULT video backend: LTX-2.3 FLF2V (dialogue/VO/audio)
│       └── prompt-composition.md          # general playbook for reference-capable backends
├── storyboard-render-loop/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── comfy_zimage.py                 # stdlib-only ComfyUI client (patch/submit/poll/download)
│   │   └── zimage_workflow.api.json        # default API-format Z-Image Turbo workflow
│   ├── agents/qa-inspect.md                # per-frame vision-QA subagent prompt
│   ├── references/
│   │   ├── comfyui-api.md                  # endpoints, workflow export, params, troubleshooting
│   │   ├── z-image-turbo.md               # image prompt playbook (shared with storyboard-prompt)
│   │   └── ltx2-video.md                   # LTX-2.3 FLF2V video prompt playbook (shared)
│   └── .env.example                        # COMFYUI_HOST for the remote GPU box
└── examples/                               # real test input/output
    ├── screenplay-writer/{input,output}.md
    └── storyboard-prompt/{input,output}.md
```

## Installation

These are portable agent skills (a `SKILL.md` with YAML frontmatter + optional
`references/`, `scripts/`, `agents/`). To make them available to an agent that discovers
skills from a directory, copy or symlink the skill folders into your skills directory, e.g.:

```powershell
Copy-Item -Recurse .\screenplay-writer      "$env:USERPROFILE\.agents\skills\"
Copy-Item -Recurse .\storyboard-prompt      "$env:USERPROFILE\.agents\skills\"
Copy-Item -Recurse .\storyboard-render-loop "$env:USERPROFILE\.agents\skills\"
```

The agent loads only a skill's name + description until a matching task triggers it, then
reads the `SKILL.md` body, and finally pulls in a `references/` file or `scripts/` only when
needed.

### Using the render loop

1. Deploy ComfyUI with Z-Image Turbo on a GPU box on your LAN (models: `qwen_3_4b`,
   `z_image_turbo_bf16`, `ae` — see `storyboard-render-loop/references/comfyui-api.md`).
2. Set the endpoint: copy `.env.example` and set `COMFYUI_HOST=http://<gpu-box>:8188`.
3. Verify targeting once: `python scripts/comfy_zimage.py --prompt "…" --out t.png --dry-run`
   (the `patch_report` should be all `true`).
4. Ask the agent to "render the storyboard for this novel excerpt" — it runs stages 1→3.

## Setup — exposing ComfyUI on the LAN (one-time, manual)

The ComfyUI server runs on a **separate GPU box** (e.g. a Windows machine) and the
agent/client runs elsewhere (e.g. a Mac) on the same network. These are manual steps
you run **on the GPU box** — they are not performed by any skill.

By default ComfyUI binds to `127.0.0.1`, so only that machine can reach it. To share it:

**On the Windows box that runs ComfyUI (models live here):**

1. Start ComfyUI listening on all interfaces:

   ```powershell
   # portable build
   .\python_embeded\python.exe -s ComfyUI\main.py --listen 0.0.0.0 --port 8188
   # or add `--listen 0.0.0.0` to the launch line inside run_nvidia_gpu.bat
   ```

2. Open the firewall port (PowerShell **as Administrator**); the active network
   profile must be Private (Public blocks inbound by default):

   ```powershell
   New-NetFirewallRule -DisplayName "ComfyUI 8188" -Direction Inbound `
     -Action Allow -Protocol TCP -LocalPort 8188 -Profile Private
   Get-NetConnectionProfile   # confirm NetworkCategory = Private
   ```

3. Find the box's LAN IP:

   ```powershell
   (Get-NetIPAddress -AddressFamily IPv4 |
     Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"}).IPAddress
   ```

**From the device that runs the agent/client (e.g. Mac) on the same LAN:**

```bash
curl http://192.168.1.50:8188/system_stats     # JSON back = reachable
export COMFYUI_HOST=http://192.168.1.50:8188
```

Gotchas:
- Both devices must be on the **same subnet** (same router/Wi-Fi; guest networks
  and AP/client isolation block peer traffic).
- Sanity-check locally first: on the Windows box, `curl http://<its-ip>:8188/system_stats`.
  If that fails, ComfyUI isn't bound to `0.0.0.0` (you missed `--listen`).
- **No auth**: ComfyUI has no authentication. Only expose it on a trusted LAN;
  never port-forward it to the public internet.

## Examples

`examples/` contains the exact prompts used to validate the writing skills and the Markdown
they produced. The two examples share the 断魂崖 beat, demonstrating the screenplay →
storyboard handoff end to end.

## Provenance & license

Design adapted from the agent prompts of `Stonewuu/ai-fusion-video` (MIT). This repository
contains original skill text and does not redistribute that project's code.
