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

Put these as a short `建议参数` line under each prompt (or once per scene if uniform):

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
建议参数：steps 9｜cfg 0｜1024×1024｜固定seed。
```

### Wide establishing action (远景 / 俯视)

```text
夜色远景俯拍，陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾；狂风卷动墨色雨线，
两名身影在崖边对峙——一名清瘦少年（短束发、粗布弟子服、左眉细疤）被击退到崖边，
一名白衣青年负手逼近，神情轻蔑。人物在环境中显得渺小，宿命压迫感。国风水墨与写实结合、
冷色调、高反差夜景、体积雾光、电影构图。画面干净，无文字、无水印、无杂乱背景。
建议参数：steps 10｜cfg 0｜1280×720｜固定seed。
```

Note how each prompt is one flowing paragraph, embeds the fixed anchor phrases for identity,
puts lighting in its own clause, and ends with the constraint line — no reference images, no
negative prompt.

## 7. First/last-frame pairs + the motion prompt

Each shot yields **two** Z-Image prompts (首帧 + 尾帧) and one motion prompt for a video model.

**How to write the pair.** Keep the two frame prompts **byte-for-byte identical except the
action/expression clause** (and, if the camera moves, the framing clause). Same anchors, same
environment, same lighting, same style, same constraints, and the **same seed** — so the two
stills read as one shot at two instants and interpolate cleanly.

```text
# 首帧 (start) — 抬腿发力前一刻
电影感全景侧面平视，二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，
冷笑抬腿正欲踹出，脚尚未触及身前踉跄的约十六岁少年，清瘦，短束发，粗布外门弟子服，
左眉有细疤；断魂崖，陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾，碎石在脚边松动。
冷调月光侧逆光拉出两人轮廓，体积雾光切开深蓝夜色。国风水墨与写实结合、冷色调、高反差
夜景、电影构图。画面干净，无文字、无水印、无多余人物，正确的手部与肢体结构。
建议参数：steps 10｜cfg 0｜1280×720｜固定seed=4477

# 尾帧 (end) — 踹中、少年越过崖线（仅动作阶段变化）
电影感全景侧面平视，二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，
收势的一脚已踹中约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，少年身体后弓、
双脚离地、正越过悬崖边线坠出；断魂崖，陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾，
碎石被踢飞。冷调月光侧逆光拉出两人轮廓，体积雾光切开深蓝夜色。国风水墨与写实结合、
冷色调、高反差夜景、电影构图。画面干净，无文字、无水印、无多余人物，正确的手部与肢体结构。
建议参数：steps 10｜cfg 0｜1280×720｜固定seed=4477

# 运镜/转场 (video, 首帧→尾帧) — 交给视频模型，不喂给 Z-Image
镜头侧面横移轻微跟随，节奏由蓄力的短暂停顿转为爆发：白衣青年抬腿、发力、一脚踹出；
少年被踹得后弓、双脚离地、越过崖线向崖外坠出。狂风骤起掀动两人衣袂与少年乱发，
碎石与墨色尘土被踢飞、向崖下卷落，体积雾光随动作翻涌。约 4 秒，前段紧绷、后段急促失重。
```

Rules of thumb:
- **Only the moment-in-time changes.** If you find yourself rewording an anchor or the lighting
  between 首帧 and 尾帧, stop — that reintroduces drift.
- **Same seed** for the pair; only randomize if the end-frame composition genuinely needs it.
- **Static shots**: make the pair differ by a micro-beat (a breath, a blink, a gaze shift) and
  write a minimal motion prompt (镜头极缓推进，人物近乎静止，只有呼吸与雾气浮动).
- **Motion prompt is backend-agnostic** (Wan2.2 FLF2V, Kling 首尾帧, Hailuo, LTX, Runway):
  describe 运镜 + 主体运动 + 环境运动 + 节奏时长. Do **not** put anchors/style/constraints in it,
  and never send it to Z-Image.
