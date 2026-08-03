---
name: storyboard-prompt
description: >-
  Convert a screenplay scene (剧本/场次) into a professional shot list (分镜脚本) and compose
  backend-agnostic image-generation prompts for each shot's 分镜图 / storyboard frame. Use
  this whenever the user wants to break a scene into shots, design 分镜 / storyboard, decide
  景别/运镜/机位 (shot size, camera movement, angle), or write prompts to generate storyboard
  reference images / keyframes for an image model — even if they just say "拆分镜", "写分镜",
  "generate storyboard prompts", "给这场戏做分镜图", or "把剧本变成分镜". For each shot it
  produces a keyframe chain (首帧…尾帧, each adjacent pair a small delta) PLUS one
  LTX-2.3 FLF2V video prompt per segment (short clips that concatenate, keeping the
  scene's narration and dialogue) to drive image-to-video. It produces the shot design AND
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

**Default video target: LTX-2.3 (Lightricks) in ComfyUI, FLF2V mode.** The keyframe-chain stills
feed its first-last-frame workflow **one segment at a time** (each adjacent pair → one short clip,
concatenated), and LTX-2.3 generates synchronized **audio incl. dialogue**, so the per-segment
video prompt carries the scene's 台词 and VO/旁白. FLF2V only interpolates cleanly across a *small*
motion, which is why a shot is chained into several short clips rather than one big jump. Read
`references/ltx2-video.md` before writing video prompts.

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
- **Express the action as a small chain of beats** (起点 → …小推进… → 落点), not one big jump —
  Pass 2 turns each beat boundary into a keyframe, and the video model only interpolates cleanly
  across small deltas. A calm shot is one beat (2 keyframes); a big move (一次跌落、蓄力到爆发)
  is 2–3 beats.
- Do **not** paste the dialogue into the description — dialogue goes in its own field as
  `角色名：台词`.
- Keep it about what's *visible*, not backstory.

**复杂度预算与拆分 (complexity budget & splitting)** — the single biggest cause of a Z-Image
frame going wrong is asking one image to hold too much. Its text encoder won't infer
relationships, and with CFG≈0 it silently drops or swaps attributes when a prompt piles up
subjects, props, and simultaneous actions. So treat **each frame as one readable image**, and
budget it before you write the prompt:

- **Per-frame budget**: aim for **≤3 anchored subjects/props that must be individually correct**
  and **one primary action**. Background crowds/objects are fine as *atmosphere* ("远处模糊的市集人群"),
  but anything that must render accurately counts against the budget.
- **If a beat exceeds the budget, split it into more shots — this is a feature, not a workaround.**
  A busy moment is naturally a *sequence*: cut it into an **establishing 全景/远景** (composition +
  where everyone is) → **中景** (the interaction) → **近景/特写** (the detail that carries the beat).
  Each resulting frame carries only what its 景别 actually shows, so every prompt stays inside the
  budget and you get better dramatic coverage for free.
- **Sub-shots when the cut is within one continuous moment**: number them `01a / 01b …` (same
  location/lighting, adjacent framings) so it's clear they belong to one story beat.
- **Demote, don't cram**: if splitting isn't wanted, move non-essential enumerated objects into a
  single atmosphere clause and let the frame breathe — a clean image of the key subjects beats a
  cluttered one that gets them wrong.
- **Last resort (single busy frame unavoidable)**: this is no longer a pure prompt problem — use a
  ComfyUI compositing approach (regional prompting / attention-couple to bind each subject to a
  region, or generate a base then inpaint subjects one at a time). Note it for the user; the skill's
  default remains split-and-anchor.

### Pass 2 — Compose the 分镜图 prompt (per shot)

Turn each shot into a natural-language image prompt for **Z-Image Turbo**. Read
`references/z-image-turbo.md` for the full playbook; the essentials:

- **One flowing paragraph, long and precise** (~80–250 words / 相应中文字数), not a keyword list.
  Z-Image Turbo's LLM text encoder rewards descriptive instruction-style prompts.
- **Layer it**: `景别/机位 + 主体 → 主体的锚点短语 → 动作/表情 → 环境/背景 → 光线 → 氛围 →
  画风 → 技术 → 约束`. Embed each entity's **anchor phrase verbatim** so identity stays stable
  across shots (no reference images are used).
- **Attribute binding for multiple subjects** — when a frame has more than one subject/prop, the
  encoder mixes up who-has-what unless you bind attributes explicitly. Keep each subject's clauses
  **grouped as one contiguous block** (anchor + clothing + action + expression together), then move
  to the next subject; don't interleave. Give each a **spatial anchor** (画面左/中/右、前景/背景、
  近/远) and **bind its action to it** (`左侧的林越攥紧玉简、抬眼；右侧的赵天骄负手冷笑`), rather
  than describing actions in a shared pile. This is the same discipline as the per-frame budget: the
  fewer subjects and the tighter each binding, the more reliably Z-Image gets them right.
- **Lighting gets its own clause** — Z-Image responds strongly to it (侧逆光、冷调月光、
  高反差夜景、体积雾光…).
- **Bake exclusions into the positive prompt** at the end (`画面干净，无文字、无水印、无多余人物`);
  the negative-prompt box is ignored by this model, so don't rely on it.
- **Style vs. content** — apply only the *style phrase*; if the art-style description names a
  concrete place/subject that conflicts with this shot, keep its look, drop its content.
- **Keyframe chain is the deliverable — not a single start/end pair.** A shot is a **chain of
  standalone Z-Image prompts `K0 → K1 → … → Kn`** (首帧 = K0, 尾帧 = Kn). Write each as a
  complete prompt, not a delta. **Why a chain, not just two frames:** the FLF2V video model
  (LTX-2.3) interpolates cleanly only when the start and end images differ by a *small* motion;
  a large jump between them morphs and warps. So each shot becomes several short clips that
  concatenate, one per adjacent keyframe pair.
- **Delta budget (beat-driven, ~2–4s per gap).** Keep every adjacent pair `Ki → Ki+1` within
  **one small continuous motion beat**. If start→end would jump a **big translation** (a fall, a
  body flung across frame), a **big pose change** (蓄力 → 爆发 → 落点), a **large camera move**, or
  you'd narrate it with a second "然后/接着", **insert an intermediate keyframe** so each pair stays
  small and interpolatable. A simple or near-static shot stays **2 keyframes (K0, K1)** = one clip;
  a busy action beat may need 3–4 keyframes = 2–3 clips.
- **Chain consistency.** Every keyframe is identical to its neighbors in everything **except the
  action/expression phase** (and framing, if the camera moves within that gap — state the shift
  explicitly in both). Same 景别 baseline, anchors verbatim, same lighting/style/constraints. The
  **whole chain shares ONE seed** so all keyframes read as the same shot. The **shared boundary
  frame `Ki` is rendered once** and reused as the end of clip *i-1* and the start of clip *i* — this
  is what makes the concatenation seamless, so never reword it between the two clips it joins.

If the user instead targets a reference-capable model (image editor / cloud API that accepts
reference images), switch to the reference-ordering rules in `references/prompt-composition.md`.

### Pass 3 — Compose the LTX-2.3 video prompts (FLF2V, one per segment)

Each **adjacent keyframe pair `Ki → Ki+1` gets its own video prompt**, so a shot with
`n+1` keyframes yields **`n` short clips** that concatenate (in order) into the finished
shot. The target is **LTX-2.3** (Lightricks) via ComfyUI's **FLF2V** (first-last-frame →
video) workflow: each clip's two Z-Image keyframes are its start/end images, and its prompt
drives the motion **and the audio**. LTX-2.3 is an audio+video model, so **this is where the
screenplay's narrative and dialogue survive into the video stage** — keep the 台词 and VO/旁白.
Read `references/ltx2-video.md` for the full playbook (large-motion limits, chaining, drift).
Keep actual video generation out of scope; you only write the prompts.

For **each segment** write **one present-tense, flowing paragraph** (a mini-screenplay, no
bullet lists) that choreographs only that segment's small beat, using temporal connectors
(随后/接着/与此同时/as/then/while). Include, in narrative order:

- **运镜 (camera)** — the shot's 景别/机位 plus the camera *move* and speed for this segment,
  related to the action ("镜头随他抬腿而侧移").
- **主体运动 (action)** — the motion across this segment's `Ki → Ki+1` gap only, with
  cause→effect and small physical detail; emotion via body language.
- **环境运动 (ambient)** — only the *moving* atmosphere (风、雾、发丝、碎屑、光闪);
  don't re-describe the frames' fixed appearance — the images already carry it.
- **音频与叙事 (audio + narrative)** — attach each line to the **segment where it actually
  occurs**, not smeared across the shot:
  - **台词** in quotation marks with **speaker + tone**, verbatim from the
    screenplay: `赵天骄冷笑着说：“一个废物，也配觊觎宗门功法？”`
  - **VO / 旁白 / 内心独白** as a tagged spoken line:
    `林越（画外音，压抑）：“我不甘心……”`
  - **环境音/音效** (风声、碎石、掌风闷响) and an optional music bed, ordered with
    the action.
- **节奏与时长 (pacing)** — echo this segment's ~2–4s and how energy changes
  (蓄力→爆发/推进→停顿).
- **Drift reinforcement** — from the **2nd clip onward, briefly restate the key subject** (a short
  identity cue, e.g. "白衣的赵天骄") so a long chain doesn't lose the character; keep it light — a
  reminder, not the full anchor.
- End with a **guardrail** clause so speech is voiced, not printed:
  `画面无字幕、无水印、无台词文字，动作连贯、无闪烁`.

Do not put the anchor phrases or the 画风/约束 image clauses in the video prompts,
and never feed these prompts to Z-Image. Keep dialogue in its original language
even if you describe motion in English (see the language note in the reference).

## Output template

Produce Markdown: a shot-list table per scene, then a block per shot containing the shot's
**keyframe chain** (K0…Kn, all sharing one seed) followed by **one LTX-2.3 video prompt per
segment** (K0→K1, K1→K2, …). A simple shot has just K0/K1 + one segment; a big-motion shot adds
intermediate keyframes and more segments.

每个提示词都**单独放进一个代码块**，复制代码块内的文字即为要喂给模型的完整提示词；
参数、说明等一律放在代码块**外**的独立段落，绝不与提示词混在一起。

````markdown
## 分镜：第 {集} 集 · {集数}-{场次} {地点}

**画风(style phrase)**：{可直接粘贴的一句话画风}
**锚点**：{角色/场景/道具名 → 不变的外观短语，逐个列出}

| 镜号 | 景别 | 时长(s) | 运镜 | 机位 | 关键帧节拍(K0→…→Kn) | 对白 | 用到的锚点 |
|----|----|------|----|----|------|----|------|
| 01 | 中景 | 4 | 慢推 | 平视 | 推门而入 → 停步 → 眼神转为震惊 | 林越：你早就知道了 | 林越/门厅 |

### 镜号 01  （关键帧链 K0–K2 → 2 个片段；全链同一 seed）

**关键帧 K0 (首帧) — Z-Image Turbo 提示词**（复制下面代码块内的文字进 CLIPTextEncode）
```
{完整自然语言提示词：景别机位+主体+锚点短语+动作起点+环境+光线+氛围+画风+约束}
```
参数（不进提示词，设在 KSampler / 空 latent 节点）：steps 9｜cfg 0｜1024×1024｜固定seed=<S>

**关键帧 K1 — Z-Image Turbo 提示词**（复制下面代码块内的文字进 CLIPTextEncode）
```
{与 K0 逐字相同，只把动作/表情推进一个小节拍（与必要的构图位移）}
```
参数（不进提示词，设在 KSampler / 空 latent 节点）：steps 9｜cfg 0｜1024×1024｜固定seed=<S>

**关键帧 K2 (尾帧) — Z-Image Turbo 提示词**（复制下面代码块内的文字进 CLIPTextEncode）
```
{与 K1 逐字相同，只把动作/表情再推进一个小节拍}
```
参数（不进提示词，设在 KSampler / 空 latent 节点）：steps 9｜cfg 0｜1024×1024｜固定seed=<S>

**片段 1 视频提示词 (LTX-2.3 FLF2V, K0→K1，含台词/旁白)**（整段喂给 LTX-2.3，绝不喂 Z-Image）
```
{一段现在时连续段落，只写这一小节拍：运镜 + 主体运动 + 环境运动 + 台词（带说话人与语气，
 引号内逐字保留）+ VO/旁白 + 环境音/音效 + 节奏(~2–4s) + 画面无字幕水印的约束}
```

**片段 2 视频提示词 (LTX-2.3 FLF2V, K1→K2，含台词/旁白)**（整段喂给 LTX-2.3，绝不喂 Z-Image）
```
{下一小节拍；第 2 段起用一句简短身份提示复述主体以抗漂移}
```
````

> **代码块里的文字就是提示词本体，代码块外的一切都不是提示词。** 关键帧代码块各自独立，逐个
> 进 Z-Image 的 CLIPTextEncode；每个`片段`视频提示词整段喂给 LTX-2.3、绝不喂 Z-Image。`参数`行
> （steps/cfg/尺寸/seed）设在 KSampler / 空 latent 节点，不是靠文字，所以放在代码块外。Z-Image
> 的文本编码器（Qwen3-4B）会把提示词里的一切当作字面文字编码，且 CFG≈0、无负向提示可抑制，一旦
> 把参数或运镜/台词描述混进图像提示词，可能被当成要画的文字/数字渲染进画面（与「无文字」冲突）。
> **整条关键帧链用同一个 seed**，相邻两帧只差一个小动作节拍，保证 FLF2V 能平滑插值；边界帧 Ki
> 只渲染一次，同时作上一片段的尾帧与下一片段的首帧，拼接才无跳变。

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
