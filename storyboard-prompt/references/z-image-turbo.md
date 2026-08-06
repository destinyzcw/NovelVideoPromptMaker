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
6. Worked examples (Chinese-source storyboard shots)
7. MiniMax-H3 reference and endpoint images
8. Scene complexity — budget, split, and bind

## 1. What makes Z-Image Turbo different

- **6B single-stream diffusion transformer (S3-DiT)**, few-step distilled "Turbo" (~8 effective
  steps). Optimized for fast, strong **instruction following**.
- Text encoder is an LLM (Qwen3-4B), so it wants **long, descriptive natural-language** prompts,
  **not** tag/keyword lists. Think "art director briefing", not "1girl, masterpiece, 8k".
- Natively supports Chinese and English. Use the **source material's primary language** for each
  image prompt and keep one language per prompt. This preserves culturally specific vocabulary;
  the separate MiniMax-H3 prompt remains English.
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
- Lin Yue: `a lean sixteen-year-old disciple with short tied hair, a coarse novice robe, and a thin scar over his left eyebrow`
- Soul-Breaking Cliff: `a steep black-rock cliff with one dead tree at the edge and bottomless cold fog below`
- damaged jade slip: `a palm-sized damaged jade slip with scorched edges and dark-gold cloud patterns`

For a permanent appearance change (injury, costume change, aging), write a **new anchor** for
that variant and use it from that shot onward — the same "variant vs. words" judgment as the
base skill, just expressed as text instead of a reference sheet.

Maintain a source-state ledger. Do not reuse a living, fully dressed, uninjured anchor for a
later stripped corpse, burned limb, bloodied face, changed costume, or newly revealed prop.
Likewise, never introduce a later state or discovery into an earlier image.

## 3. No negative prompt → in-prompt constraints

State exclusions as positive constraints at the **end** of the prompt. The strong
instruction-following still respects explicit `without` phrasing even without CFG. Useful clauses
for clean storyboard frames:

- `Clean frame without text, watermark, or logo.`
- `Only the described characters are present; the background remains uncluttered.`
- `Anatomically correct hands and limbs with the correct number of fingers.`
- `Sharp focus without motion blur.` (unless motion blur is wanted)

Only add the constraints that matter for the shot — don't paste a boilerplate wall every time.
If readable text is required by the source, quote the exact text and omit any blanket `no text`
constraint for that image.

## 4. Prompt scaffold (layered)

Z-Image responds best to a clear, layered order. Compose each shot's prompt as:

`[shot size/angle + subject] → [identity anchor] → [action/expression] → [environment] → [lighting] → [atmosphere] → [style/medium] → [technical treatment] → [constraints]`

- Lead with shot type + subject, fold in the **anchor phrase** for identity.
- **Lighting deserves its own clause** — Z-Image reacts strongly to it (侧逆光、冷调月光、
  高反差夜景、体积雾光…).
- End with medium/style (画风) and the constraint clause.
- Target **~80–250 words** (中文相应字数). Long *and precise* wins; poetic/novelistic loses.
  Hard cap ~512 tokens by default.

## 5. Recommended image parameters

Put the prompt paragraph in the JSON image input's `prompt` string. Put generation settings in
the sibling `parameters` object; never append sampler settings to the prompt text:

- **steps**: 8–12 (native ≈ 8; raise only if you see noise)
- **cfg / guidance**: 0–1 (base Turbo uses 0; some ComfyUI wrappers expect 1)
- **negative prompt**: leave empty — it is ignored
- **resolution**: 1024×1024 native; use aspect ratios near that (e.g. 1280×720 for 16:9 shots)
- **seed**: fix a seed while tuning a shot's prompt so you compare *prompt* changes, not noise;
  randomize when you want alternates
- **sampler/scheduler**: follow the Z-Image Turbo ComfyUI workflow defaults

## 6. Worked examples (Chinese-source storyboard shots)

### Emotional close-up (特写 / 慢推)

```text
电影感特写画面，一名身形清瘦的十六岁弟子占据画面中心。他束着短发，身穿粗布
入门弟子袍，左眉上方有一道细疤，嘴角带血，雨水与尘土划过面庞，神情由倔强转为
坚定。发白的指节紧握一枚巴掌大小、边缘焦黑破损并带有暗金云纹的玉简。冷月光从
背后勾勒人物轮廓，夜色悬崖与雾气在浅景深中虚化。写实中国水墨质感，冷色电影
调色，细腻胶片颗粒。画面干净，不出现文字、水印或多余人物。
```
Parameters: `{"steps": 9, "cfg": 0, "width": 1024, "height": 1024, "seed": 2301}`

### Wide establishing action (远景 / 俯视)

```text
夜晚俯视远景，陡峭的黑色岩崖占据画面，崖边只有一棵枯树，下方是深不见底的寒雾。
狂风卷着冰冷暴雨横扫两个人物：束短发、穿粗布袍、左眉有细疤的清瘦少年弟子在
悬崖边踉跄；一名白袍青年双手负于身后，以轻蔑目光步步逼近。两人在宏大险峻的
山崖景观中保持较小比例。写实中国水墨质感，冷色调，高反差夜景照明，体积雾与
电影化构图。画面干净，不出现文字、水印或杂乱背景元素。
```
Parameters: `{"steps": 10, "cfg": 0, "width": 1280, "height": 720, "seed": 2302}`

Note how each prompt is one flowing paragraph, embeds the fixed anchor phrases for identity,
puts lighting in its own clause, and ends with the constraint line — no reference images, no
negative prompt. Parameters always remain separate from the prompt string.

## 7. MiniMax-H3 reference and endpoint images

For the default character-driven **Ref2VA** workflow, render the critical images selected by the
storyboard plan. They may show character identity, costume, setting/style, a key prop, facial
detail, or any decisive action/composition moment in the video. Name them R1...Rn, map each to
`reference_image`, and describe each role explicitly in the H3 prompt. They do not need to depict
the first or last frame, and they receive no timeline timestamp.

Use at most two strong, complementary references per H3 video piece. If more critical visual
facts are required, split the action into multiple coherent pieces rather than dropping essential
state or overloading a reference image.
Keep shared identity and visual-world anchors verbatim across their source-language prompts.
Do not rely on generic portraits alone when the target action depends on injuries, props,
spatial relationships, group geometry, or decisive poses. Generate targeted critical stills.

For an FL2VA workflow that truly needs exact endpoints, render two Z-Image frames:

- **K0 / Picture 1** — exact opening state at 0.00 seconds.
- **K1 / Picture 2** — exact ending state at the declared 4–15 second endpoint.

Keep them consistent in identity, clothing, environment, aspect ratio, style, and lighting.
Describe a reachable opening and ending state; the H3 prompt supplies the observable intermediate
motion path. H3 accepts only one first frame and one last frame per request, so intermediate
storyboard images are planning aids, not extra FL2VA API inputs.

For a large viewpoint change, location change, or several unrelated actions, create another shot
and another H3 request. Do not recreate the old pattern of several 2–4 second interpolation clips:
H3's minimum output duration is 4 seconds and its official FL2VA guide favors one continuous shot.

K0 / Picture 1 — just before the kick:

```text
A cinematic medium-close side view at eye level shows a tall white-robed young man with tied hair,
sharp eyes, and a silver-trimmed sect robe raising one leg with a cold smile, just before his boot
touches a staggering lean sixteen-year-old disciple with short tied hair, a coarse novice robe,
and a thin scar over his left eyebrow. They stand on a steep black-rock cliff with one dead tree
at the edge and bottomless cold fog below; gravel loosens beneath their feet. Cool moonlight rims
both figures as volumetric fog cuts through the deep-blue night. Realistic Chinese ink-wash
treatment, cool palette, high contrast, cinematic composition. Clean frame without text,
watermark, or extra people; anatomically correct hands and limbs.
```
Parameters: `{"steps": 10, "cfg": 0, "width": 1280, "height": 720, "seed": 4477}`

K1 / Picture 2 — the disciple falling beyond the cliff edge:

```text
A cinematic high-angle wide shot looks beyond the cliff edge. A tall white-robed young man with
tied hair and a silver-trimmed sect robe stands at the rim after retracting his kick. Below him,
a lean sixteen-year-old disciple with short tied hair, a coarse novice robe, and a thin scar over
his left eyebrow clutches the damaged jade slip while falling into open air and rotating off
balance. Loose stones tumble into bottomless cold fog beside the steep black-rock cliff and its
single dead tree. Cool rim moonlight and rising volumetric fog shape the deep-blue night.
Realistic Chinese ink-wash treatment, cool palette, high contrast, cinematic composition.
Clean frame without text, watermark, or extra people; anatomically correct limbs.
```
Parameters: `{"steps": 10, "cfg": 0, "width": 1280, "height": 720, "seed": 4477}`

Leave camera motion, action progression, dialogue, and sound to MiniMax-H3 (see
`minimax-h3-video.md`), not Z-Image. Picture 1 and Picture 2 only anchor the endpoints;
the H3 prompt describes the complete continuous path:

```text
Picture 1's prepared pose → the leg drives forward → the kick lands → Lin Yue's torso bends and
both feet leave the ground → he crosses the cliff edge → Picture 2's falling composition. One
continuous six-second shot.
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

For a multi-party confrontation, generate several spatially bound subgroup or composition
references instead of asking one image to render every named person accurately. Every speaking
or decisive subject still needs a clear identity reference.

**Split instead of cram.** A busy moment is a *sequence*, not one image — cut it into
establishing 全景/远景 → 中景 → 近景/特写 (or sub-shots `01a/01b` within one continuous beat, same
location & lighting). Each frame then only describes what its 景别 shows, so every prompt stays in
budget. This is the primary fix and it improves coverage.

**Bind attributes when >1 subject shares a frame.** Keep each subject's clauses as one contiguous
block (anchor + clothing + action + expression), don't interleave; give each a spatial anchor and
bind its action to it:

```text
On the left, a lean sixteen-year-old disciple with short tied hair, a coarse novice robe, and a
thin scar over his left eyebrow kneels while gripping the damaged jade slip and glaring upward.
On the right, a white-robed young man with tied hair and a silver-trimmed sect robe stands with
his hands behind his back, looking down with a cold smile.
```
Grouping + 左/右/前景/背景 + per-subject actions is what stops the model from mixing them up.

**Last resort — a single busy frame is unavoidable.** This is no longer a prompt problem: use a
ComfyUI compositing approach — **regional prompting / attention-couple** (bind each subject to a
mask/region), or **generate a base then inpaint** subjects one at a time. Heavier to set up; the
project default stays split-and-anchor.
