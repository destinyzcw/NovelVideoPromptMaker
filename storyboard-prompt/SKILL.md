---
name: storyboard-prompt
description: >-
  Convert a screenplay scene (剧本/场次) into a professional shot list (分镜脚本) and compose
  backend-agnostic image-generation prompts for each shot's 分镜图 / storyboard frame. Use
  this whenever the user wants to break a scene into shots, design 分镜 / storyboard, decide
  景别/运镜/机位 (shot size, camera movement, angle), or write prompts to generate storyboard
  reference images / keyframes for an image model — even if they just say "拆分镜", "写分镜",
  "generate storyboard prompts", "给这场戏做分镜图", or "把剧本变成分镜". For each shot it
  produces a start-frame (首帧) and end-frame (尾帧) image prompt PLUS an LTX-2.3
  FLF2V video prompt (keeping the scene's narration and dialogue) to drive
  image-to-video between them. It produces the shot design AND
  the text prompts, but does NOT call any specific image/video model — you hand the
  prompts to whatever backend you use. Default target is Z-Image Turbo in ComfyUI. This is the
  second stage after the screenplay-writer skill. Also trigger on "z-image", "z-image-turbo",
  "ComfyUI 分镜/提示词", "给分镜写提示词", or turning a scene into image-gen prompts.
---

# Storyboard Prompt Generator (分镜图 prompt)

Turn a written scene into (1) a **shot list** — how a director breaks the scene into shots —
and (2) a **ready-to-use image prompt** for each shot's reference frame (分镜图). This skill
deliberately stops at the prompt: the shot-design logic is **backend-agnostic**, and only the
final prompt wording is tuned per image model.

**Default target: Z-Image Turbo (Tongyi-MAI) in ComfyUI.** Its behavior drives the prompt
style, so read `references/z-image-turbo.md` before composing prompts. The three things that
matter most: it is **text-to-image** (no reference-image input → carry identity with words),
it **ignores negative prompts** (CFG=0 → bake exclusions into the positive prompt), and it wants
**long, precise natural-language** prompts, not tag lists. If the user targets a different model
(e.g. a reference-capable editor or a cloud API), fall back to the general multi-backend playbook
in `references/prompt-composition.md`.

**Default video target: LTX-2.3 (Lightricks) in ComfyUI, FLF2V mode.** The 首帧/尾帧 stills feed
its first-last-frame workflow, and LTX-2.3 generates synchronized **audio incl. dialogue**, so the
per-shot video prompt carries the scene's 台词 and VO/旁白. Read `references/ltx2-video.md` before
writing video prompts.

Two things make good storyboards hard: choosing shots that serve the drama, and keeping
character/scene appearance **consistent** across shots and episodes. This skill encodes both.

## Prerequisites — establish the visual bible first

Before designing shots, make sure you have (ask the user or infer from the screenplay):

- **Art style (画风)** — the project's overall look: medium, palette, rendering style, mood.
  Every shot prompt inherits this as a style clause. Keep a one-line **style phrase** you can
  paste verbatim into each prompt.
- **Consistency anchors** — for each character / scene / prop write one short, invariant physical
  description (the **anchor phrase**) and reuse it *verbatim* in every prompt that entity appears
  in. Because the default backend (Z-Image Turbo) is text-to-image with no reference-image input,
  these anchors are what keep a face or location from drifting shot to shot. Paraphrasing an
  anchor is the top cause of drift — decide it once, then don't reword it.
- **Appearance variants** — decide which entities need a *separate anchor* because their look
  changes materially: injury, disability, aging, major costume change, a scene's destruction or
  transformation. Do **not** make a variant for mere expression, emotion, simple actions, or
  lighting — those are handled with words in the shot description. Rule of thumb: *if you'd have
  to redraw the character to show the change, write a new anchor; otherwise reuse the base one.*
  Bias toward reuse — fewer anchors means better consistency.

## Workflow

### Pass 1 — Shot design (per scene)

Read the scene, then break it into shots. Let the drama pick the coverage:

- **Dialogue scenes** → shot/reverse-shot (正反打), alternating 近景 and 中景.
- **Action scenes** → 跟拍 / 手持, fast cuts, quickly changing 景别.
- **Emotional beats** → 特写 + slow push-in (慢推), longer duration.
- **Scene changes** → transition (叠化 / 黑场).

Typical scene = **3–15 shots**, each **2–10 seconds**. Give an important line its own shot.
Cover the whole scene — every beat of action and every key line should appear somewhere.

For each shot decide: **景别** (远景/全景/中景/近景/特写), **时长**, **运镜** (camera movement:
固定/推/拉/摇/移/跟/手持…), **机位/角度** (camera angle: 平视/俯视/仰视/过肩…), **画面描述
(content)**, **对白**, and which character/scene/prop **anchors** it uses (by name).

**Writing the 画面描述 (content)** — this is the semantic core of the shot and the seed of the
image prompt:
- Describe composition, the subject's action and expression, and environment/atmosphere
  consistent with the scene.
- Do **not** paste the dialogue into the description — dialogue goes in its own field as
  `角色名：台词`.
- Keep it about what's *visible*, not backstory.

### Pass 2 — Compose the 分镜图 prompt (per shot)

Turn each shot into a natural-language image prompt for **Z-Image Turbo**. Read
`references/z-image-turbo.md` for the full playbook; the essentials:

- **One flowing paragraph, long and precise** (~80–250 words / 相应中文字数), not a keyword list.
  Z-Image Turbo's LLM text encoder rewards descriptive instruction-style prompts.
- **Layer it**: `景别/机位 + 主体 → 主体的锚点短语 → 动作/表情 → 环境/背景 → 光线 → 氛围 →
  画风 → 技术 → 约束`. Embed each entity's **anchor phrase verbatim** so identity stays stable
  across shots (no reference images are used).
- **Lighting gets its own clause** — Z-Image responds strongly to it (侧逆光、冷调月光、
  高反差夜景、体积雾光…).
- **Bake exclusions into the positive prompt** at the end (`画面干净，无文字、无水印、无多余人物`);
  the negative-prompt box is ignored by this model, so don't rely on it.
- **Style vs. content** — apply only the *style phrase*; if the art-style description names a
  concrete place/subject that conflicts with this shot, keep its look, drop its content.
- **Keyframes are the deliverable, not an afterthought.** Every shot produces **two full,
  standalone Z-Image Turbo prompts** — a **首帧 (start frame)** at the action's opening phase
  (动作开始前 / 刚发力 / 情绪起点) and a **尾帧 (end frame)** at its resolved phase (动作完成后的
  结果 / 情绪落点). Write them as complete prompts, not deltas. They must be **identical in
  everything except the action/expression phase** — same 景别 baseline, same anchor phrases
  verbatim, same environment, same lighting clause, same style clause, same constraints — so the
  two frames read as the same shot and can be interpolated by a video model. Only the moment-in-
  time changes (and, if 运镜 moves the camera, the framing may shift start→end; state that shift
  explicitly in both prompts). Reuse the **same seed** for 首帧 and 尾帧 so they stay visually
  coherent. For a genuinely static shot, the two prompts differ only by a micro-beat (a breath, a
  gaze shift) — say so rather than duplicating verbatim.

If the user instead targets a reference-capable model (image editor / cloud API that accepts
reference images), switch to the reference-ordering rules in `references/prompt-composition.md`.

### Pass 3 — Compose the LTX-2.3 video prompt (FLF2V, per shot)

Each shot also gets one **video prompt** that animates 首帧 → 尾帧. The target is
**LTX-2.3** (Lightricks) via ComfyUI's **FLF2V** (first-last-frame → video)
workflow: the two Z-Image frames are the start/end images, and this prompt drives
the motion **and the audio**. LTX-2.3 is an audio+video model, so **this is where
the screenplay's narrative and dialogue survive into the video stage** — keep the
台词 and VO/旁白. Read `references/ltx2-video.md` for the full playbook. Keep
actual video generation out of scope; you only write the prompt.

Write **one present-tense, flowing paragraph** (a mini-screenplay, no bullet
lists) that choreographs the beat, using temporal connectors (随后/接着/与此同时/
as/then/while). Include, in narrative order:

- **运镜 (camera)** — the shot's 景别/机位 plus the camera *move* and speed,
  related to the action ("镜头随他抬腿而侧移").
- **主体运动 (action)** — the motion across the gap between 首帧 and 尾帧, with
  cause→effect and small physical detail; emotion via body language.
- **环境运动 (ambient)** — only the *moving* atmosphere (风、雾、发丝、碎屑、光闪);
  don't re-describe the frames' fixed appearance — the images already carry it.
- **音频与叙事 (audio + narrative)** — the core reason to keep dialogue:
  - **台词** in quotation marks with **speaker + tone**, verbatim from the
    screenplay: `赵天骄冷笑着说：“一个废物，也配觊觎宗门功法？”`
  - **VO / 旁白 / 内心独白** as a tagged spoken line:
    `林越（画外音，压抑）：“我不甘心……”`
  - **环境音/音效** (风声、碎石、掌风闷响) and an optional music bed, ordered with
    the action.
- **节奏与时长 (pacing)** — echo the shot's 时长 and how energy changes
  (蓄力→爆发/推进→停顿).
- End with a **guardrail** clause so speech is voiced, not printed:
  `画面无字幕、无水印、无台词文字，动作连贯、无闪烁`.

Do not put the anchor phrases or the 画风/约束 image clauses in the video prompt,
and never feed this prompt to Z-Image. Keep dialogue in its original language
even if you describe motion in English (see the language note in the reference).

## Output template

Produce Markdown: a shot-list table per scene, then a block per shot containing the two frame
prompts and the LTX-2.3 video prompt.

```markdown
## 分镜：第 {集} 集 · {集数}-{场次} {地点}

**画风(style phrase)**：{可直接粘贴的一句话画风}
**锚点**：{角色/场景/道具名 → 不变的外观短语，逐个列出}

| 镜号 | 景别 | 时长(s) | 运镜 | 机位 | 画面描述(首→尾) | 对白 | 用到的锚点 |
|----|----|------|----|----|------|----|------|
| 01 | 中景 | 4 | 慢推 | 平视 | 林越推门而入 → 停步，眼神从警惕转为震惊 | 林越：你早就知道了 | 林越/门厅 |

### 镜号 01
**首帧 (start) — Z-Image Turbo 提示词**
{完整自然语言提示词：景别机位+主体+锚点短语+动作起点+环境+光线+氛围+画风+约束}
建议参数：steps 9｜cfg 0｜1024×1024｜固定seed=<S>

**尾帧 (end) — Z-Image Turbo 提示词**
{完整自然语言提示词：与首帧逐字相同，只改动作/表情阶段（与必要的构图位移）}
建议参数：steps 9｜cfg 0｜1024×1024｜固定seed=<S>

**LTX-2.3 视频提示词 (FLF2V, 首帧→尾帧，含台词/旁白)**
{一段现在时连续段落：运镜 + 主体运动 + 环境运动 + 台词（带说话人与语气，引号内逐字保留）
 + VO/旁白 + 环境音/音效 + 节奏时长 + 画面无字幕水印的约束}
```

> **只有两段「首帧/尾帧」提示词进入 Z-Image 的 CLIPTextEncode。** `建议参数` 是给采样器的
> （steps/cfg/尺寸/seed 在 KSampler / 空 latent 节点设置，不是靠文字），`LTX-2.3 视频提示词`
> 是给 LTX-2.3 视频模型的、绝不喂给 Z-Image。Z-Image 的文本编码器（Qwen3-4B）会把提示词里的
> 一切当作字面文字编码，且 CFG≈0、无负向提示可抑制，一旦把 `建议参数` 或运镜/台词描述留在
> 图像提示词里，可能被当成要画的文字/数字渲染进画面（与「无文字」冲突）。务必分行、分开传递。
> 首帧与尾帧用**同一个 seed**，以保证是同一镜头的两个瞬间；LTX-2.3 用这两帧作首/尾帧插值。

## Consistency rules (why they matter)

- **Reuse anchor phrases verbatim** so a character/location looks identical across shots. Match
  by the screenplay's canonical names; if no variant anchor applies, use the base one. With a
  text-to-image backend, the words *are* the only continuity mechanism.
- **Variants sparingly** — over-splitting a character into many look-alike anchors destroys
  continuity. Words handle transient changes (expression, blood, wet hair); a new anchor is only
  for permanent look changes.
- **Style vs. content separation** — the style phrase sets *look*, never *scene content*.
  Mixing them is the top cause of a storyboard frame ignoring the actual shot.

For the Z-Image Turbo prompt playbook (anchors, in-prompt constraints, layered scaffold, ComfyUI
parameters, worked examples) read `references/z-image-turbo.md`. For the LTX-2.3 video prompt
playbook (FLF2V, present-tense mini-screenplay, dialogue/VO/audio syntax, guardrails, worked
example) read `references/ltx2-video.md`. For other image backends that accept reference images,
read the general playbook in `references/prompt-composition.md`.
