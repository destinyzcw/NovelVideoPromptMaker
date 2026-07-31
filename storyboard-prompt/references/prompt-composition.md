# Image-prompt composition — reference

The full playbook for turning a shot into a 分镜图 image prompt. Read this when composing
prompts, handling reference images, or targeting a specific backend's capabilities.

## Table of contents
1. Prompt structure (priority order)
2. Reference-image ordering rules
3. Model-capability fallback (no reference-image support)
4. First-frame vs last-frame keyframes
5. Style/content conflict handling
6. Worked examples

## 1. Prompt structure (priority order)

Build each prompt in this order of priority, highest first:

1. **Shot content (画面描述)** — the subject, action, expression, composition of *this* shot.
   This is non-negotiable; it defines the picture.
2. **Art style (画风)** — medium, palette, rendering, overall mood/texture. Inherited from the
   project, applied to every shot.
3. **Shot grammar** — translate 景别/机位/运镜 into visual language: 特写 → tight framing on the
   face; 俯视 → high angle looking down; 慢推 → implied inward focus / shallow depth.
4. **Environment & lighting** — time of day, weather, key light direction, atmosphere consistent
   with the scene heading.

Write it as flowing natural Chinese describing the finished picture — not a comma-salad of tags.

## 2. Reference-image ordering rules

Most image models read `imageUrls` positionally (图片1, 图片2, …). When your backend supports
reference images:

- **Position 1 = art-style reference** (if you have one). Begin the prompt with an explicit
  guard so the model copies only the look:
  `仅参考图片1的画面风格，绝不参考其中的任何物品和构图，`
- **Positions 2+ = subject references** — character, then props, then scene — in a fixed order.
  Reference them by number in the prompt text (`图片2为林越的相貌，图片3为门厅`).
- **Cap at ~5 references total.** Beyond that, models blur identities; drop the least important.
- **White-background asset sheets**: instruct the model to strip the pure-white background so the
  subject blends naturally into the shot's environment
  (`剥离图片2的纯白背景，使人物自然融入雨夜门厅`).

## 3. Model-capability fallback (no reference-image support)

If the target model does not accept reference images:

- Do **not** pass image URLs, and do **not** retry the unsupported parameter.
- Transcribe the needed identity into words: the art style, the character's key features (发型、
  五官、体型、服装), prop appearance, and scene look all go into the text prompt.
- Accept slightly weaker cross-shot consistency and compensate by describing the same fixed
  features with the same wording every time (a consistency "anchor phrase" per character).

## 4. First-frame vs last-frame keyframes

When a shot will drive a video (image-to-video), you often need two stills:

- **First frame (首帧 / first)** — the opening freeze: the moment *before* the action starts or
  just as it begins. Emphasize the pre-action pose and setup.
- **Last frame (尾帧 / last)** — the closing freeze: the *result* after the action completes.
  Emphasize the outcome state.

Both inherit the same art style, character references, and scene; only the described moment
differs. Keep the core content prompt identical and swap just the action-phase clause.

## 5. Style/content conflict handling

The art-style reference often depicts its own scene/subject. Never let that leak into the shot:

- Extract only **style and texture** from it — brushwork, palette, grain, lighting quality.
- If the art-style description names a concrete place, object, or character that clashes with the
  current shot, explicitly ignore that content and keep only the rendering feel.
- This separation is the single biggest lever for storyboard-frame quality; state it in the
  prompt rather than assuming the model infers it.

## 6. Worked examples

### With reference images

Shot: `特写 / 慢推 / 平视`　画面描述: 林越眼神从警惕转为震惊　参考: 画风图、林越(初始)

```text
仅参考图片1的画面风格，绝不参考其中的任何物品和构图，
画面为林越面部特写，镜头缓缓推近，他的眼神由警惕逐渐转为震惊，眉头先皱后骤然睁大；
图片2为林越的相貌，剥离其纯白背景；雨夜门厅昏黄暖光自侧上方打来，背景虚化，
整体保持图片1的胶片颗粒质感与低饱和冷暖对比。
```

### No reference-image support (features transcribed)

```text
电影感胶片质感、低饱和冷暖对比、颗粒感的画面风格；
林越面部特写：约三十岁男性，短硬寸头、剑眉、下颌有旧疤，深色风衣；
镜头缓缓推近，眼神由警惕转为震惊；雨夜门厅昏黄暖光自侧上方打来，背景虚化。
```

### First / last frame pair (for video)

- 首帧：`……林越的手刚触到门把，尚未推开，动作定格于开始前的一瞬……`
- 尾帧：`……门已推开，林越半身探入门厅，雨水正从风衣下摆滴落，定格于动作完成后……`
