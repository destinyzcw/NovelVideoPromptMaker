# Target backend — Z-Image Turbo (ComfyUI)

The default image backend for this project is **Z-Image Turbo** (Tongyi-MAI) run in ComfyUI.
It behaves very differently from classic Stable Diffusion, so prompts must be composed for it
specifically. Read this whenever you generate 分镜图 prompts intended for Z-Image Turbo.

## Table of contents
1. What makes Z-Image Turbo different
2. No reference images → consistency anchors
3. No negative prompt → in-prompt constraints
4. Prompt scaffold (layered)
5. Recommended ComfyUI parameters
6. Worked examples (Chinese, storyboard shots)
7. Keyframe chain + per-segment motion prompts
8. Scene complexity — budget, split, and bind

## 1. What makes Z-Image Turbo different

- **6B single-stream diffusion transformer (S3-DiT)**, few-step distilled "Turbo" (~8 effective
  steps). Optimized for fast, strong **instruction following**.
- Text encoder is an LLM (Qwen3-4B), so it wants **long, descriptive natural-language** prompts,
  **not** tag/keyword lists. Think "art director briefing", not "1girl, masterpiece, 8k".
- **Bilingual** (中文 + English) for both prompt understanding and text rendering — Chinese
  prompts are first-class, which suits 国风 / 修仙 storyboards. Keep one language per prompt.
- **No classifier-free guidance at inference** (`guidance_scale = 0`); the base pipeline
  **ignores `negative_prompt` entirely**. What you don't say is allowed; what you say vaguely,
  it improvises.
- Base Turbo is **text-to-image**: it does **not** accept character/scene reference images. So
  cross-shot consistency can't lean on reference sheets — it must be carried by words.

## 2. No reference images → consistency anchors

Because you can't feed a character sheet, keep a character/scene/prop looking the same across
shots by reusing a fixed **anchor phrase** — a short, invariant physical description — verbatim
in every prompt that entity appears in. Decide the anchor once (from the visual bible) and don't
paraphrase it shot to shot; paraphrasing is what makes a face drift.

Example anchors:
- 林越（初始）：`约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤`
- 断魂崖：`陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾`
- 残破玉简：`巴掌大的残破玉简，边缘焦黑，表面暗金云纹`

For a permanent appearance change (injury, costume change, aging), write a **new anchor** for
that variant and use it from that shot onward — the same "variant vs. words" judgment as the
base skill, just expressed as text instead of a reference sheet.

## 3. No negative prompt → in-prompt constraints

State exclusions as positive constraints at the **end** of the prompt. The strong
instruction-following still respects "无/不要/without" phrasing even without CFG. Useful clauses
for clean storyboard frames:

- `画面干净，无文字、无水印、无logo`
- `无多余人物、无杂乱背景`
- `正确的手部与肢体结构，无多余手指`
- `实焦清晰，无运动模糊`（unless motion blur is wanted for an action shot）

Only add the constraints that matter for the shot — don't paste a boilerplate wall every time.

## 4. Prompt scaffold (layered)

Z-Image responds best to a clear, layered order. Compose each shot's prompt as:

`[景别/机位 + 主体] → [主体外观锚点] → [动作/表情] → [环境/背景] → [光线] → [氛围] → [画风/媒介] → [技术] → [约束]`

- Lead with shot type + subject, fold in the **anchor phrase** for identity.
- **Lighting deserves its own clause** — Z-Image reacts strongly to it (侧逆光、冷调月光、
  高反差夜景、体积雾光…).
- End with medium/style (画风) and the constraint clause.
- Target **~80–250 words** (中文相应字数). Long *and precise* wins; poetic/novelistic loses.
  Hard cap ~512 tokens by default.

## 5. Recommended ComfyUI parameters

Keep the prompt paragraph inside its own code block and put these as a separate `参数（不进提示词）`
line **outside** the code block (they go on KSampler / empty-latent nodes, never into the text):

- **steps**: 8–12 (native ≈ 8; raise only if you see noise)
- **cfg / guidance**: 0–1 (base Turbo uses 0; some ComfyUI wrappers expect 1)
- **negative prompt**: leave empty — it is ignored
- **resolution**: 1024×1024 native; use aspect ratios near that (e.g. 1280×720 for 16:9 shots)
- **seed**: fix a seed while tuning a shot's prompt so you compare *prompt* changes, not noise;
  randomize when you want alternates
- **sampler/scheduler**: follow the Z-Image Turbo ComfyUI workflow defaults

## 6. Worked examples (storyboard shots, Chinese)

### Emotional close-up (特写 / 慢推)

```text
电影感特写，镜头缓缓推近一名约十六岁少年——清瘦，短束发，粗布外门弟子服，左眉有细疤；
他嘴角带血，雨水混着尘土划过脸颊，眼神由不甘转为坚定，指节发白地攥紧怀中一枚巴掌大的
残破玉简（边缘焦黑、暗金云纹）。背景为断魂崖夜色，冷调月光自侧后方勾出轮廓，浅景深虚化
崖雾。国风水墨与写实结合、冷色调、电影质感、胶片颗粒。画面干净，无文字、无水印、无多余人物。
```
参数（不进提示词）：steps 9｜cfg 0｜1024×1024｜固定seed。

### Wide establishing action (远景 / 俯视)

```text
夜色远景俯拍，陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾；狂风卷动墨色雨线，
两名身影在崖边对峙——一名清瘦少年（短束发、粗布弟子服、左眉细疤）被击退到崖边，
一名白衣青年负手逼近，神情轻蔑。人物在环境中显得渺小，宿命压迫感。国风水墨与写实结合、
冷色调、高反差夜景、体积雾光、电影构图。画面干净，无文字、无水印、无杂乱背景。
```
参数（不进提示词）：steps 10｜cfg 0｜1280×720｜固定seed。

Note how each prompt is one flowing paragraph, embeds the fixed anchor phrases for identity,
puts lighting in its own clause, and ends with the constraint line — no reference images, no
negative prompt. The `参数` line always lives **outside** the code block.

## 7. MiniMax-H3 endpoint frames

For the default MiniMax-H3 FL2VA workflow, each shot normally needs two rendered Z-Image frames:

- **K0 / Picture 1** — exact opening state at 0.00 seconds.
- **K1 / Picture 2** — exact ending state at the declared 4–15 second endpoint.

Keep them consistent in identity, clothing, environment, aspect ratio, style, and lighting.
Describe a reachable opening and ending state; the H3 prompt supplies the observable intermediate
motion path. H3 accepts only one first frame and one last frame per request, so intermediate
storyboard images are planning aids, not extra FL2VA API inputs.

For a large viewpoint change, location change, or several unrelated actions, create another shot
and another H3 request. Do not recreate the old pattern of several 2–4 second interpolation clips:
H3's minimum output duration is 4 seconds and its official FL2VA guide favors one continuous shot.

K0 (首帧) — 抬腿发力前一刻：

```text
电影感中近景侧面平视，二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，
冷笑抬腿正欲踹出，脚尚未触及身前踉跄的约十六岁少年，清瘦，短束发，粗布外门弟子服，
左眉有细疤；断魂崖，陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾，碎石在脚边松动。
冷调月光侧逆光拉出两人轮廓，体积雾光切开深蓝夜色。国风水墨与写实结合、冷色调、高反差
夜景、电影构图。画面干净，无文字、无水印、无多余人物，正确的手部与肢体结构。
```
参数（不进提示词）：steps 10｜cfg 0｜1280×720｜固定seed=4477

K1 (尾帧 / Picture 2) — 少年越过崖线、坠入冷雾：

```text
电影感远景高角度俯视，二十岁左右白衣青年，身形修长，玉冠束发，银纹宗门长袍，立在崖边
收势；约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，抱紧玉简越过崖线、整个人
向崖外坠出、在空中失衡旋转；断魂崖，陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾，
碎石随之滚落坠入雾中。冷调月光侧逆光，体积雾光向上翻卷。国风水墨与写实结合、冷色调、
高反差夜景、电影构图。画面干净，无文字、无水印、无多余人物，正确的手部与肢体结构。
```
参数（不进提示词）：steps 10｜cfg 0｜1280×720｜固定seed=4477

运镜、动作过程、台词与声音交给 MiniMax-H3（见 `minimax-h3-video.md`），不喂给
Z-Image。Picture 1 和 Picture 2 只锚定端点，H3 prompt 写完整连续路径：

```text
Picture 1 的蓄力状态 → 抬腿发力 → 踹击命中 → 林越身体后弓、双脚离地 →
越过崖线 → Picture 2 的坠落构图。总时长 6 秒，单镜头连续完成。
```

Rules of thumb:
- Keep endpoint anchors, environment, style, lighting, and aspect ratio consistent.
- A shared seed can help Z-Image continuity, but it is a still-generation tactic, not an H3 field.
- Static shots still need a visible micro-development: breath, blink, gaze shift, focus pull,
  steam, fabric, or light movement.
- If endpoint states cannot be connected credibly in 4–15 seconds from one camera setup, split
  the screenplay beat into separate shots.
- Never send H3 alignment instructions, dialogue tags, soundscape, music, or API parameters to
  Z-Image.

## 8. Scene complexity — budget, split, and bind

The most common failure mode is **one frame carrying too much**. Z-Image's encoder reads the whole
paragraph literally and won't infer relationships; with CFG≈0 there's no negative prompt to rescue
you, so a prompt stuffed with many subjects, props, and simultaneous actions makes the model **drop
or swap attributes** (wrong clothes on the wrong person, missing props, merged bodies). Length alone
isn't the problem — the sweet spot is ~80–250 words — *element density* is.

**Budget every frame.** Aim for **≤3 subjects/props that must each render correctly** and **one
primary action** per image. Background crowds/objects are free as *atmosphere* words
(`远处模糊的市集人群`), but anything that must be accurate counts.

**Split instead of cram.** A busy moment is a *sequence*, not one image — cut it into
establishing 全景/远景 → 中景 → 近景/特写 (or sub-shots `01a/01b` within one continuous beat, same
location & lighting). Each frame then only describes what its 景别 shows, so every prompt stays in
budget. This is the primary fix and it improves coverage.

**Bind attributes when >1 subject shares a frame.** Keep each subject's clauses as one contiguous
block (anchor + clothing + action + expression), don't interleave; give each a spatial anchor and
bind its action to it:

```text
画面左侧，约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，半跪着攥紧怀中残破玉简、抬眼瞪视；
画面右侧，二十岁左右白衣青年，玉冠束发，银纹宗门长袍，负手而立、居高临下地冷笑。
```
Grouping + 左/右/前景/背景 + per-subject actions is what stops the model from mixing them up.

**Last resort — a single busy frame is unavoidable.** This is no longer a prompt problem: use a
ComfyUI compositing approach — **regional prompting / attention-couple** (bind each subject to a
mask/region), or **generate a base then inpaint** subjects one at a time. Heavier to set up; the
project default stays split-and-anchor.
