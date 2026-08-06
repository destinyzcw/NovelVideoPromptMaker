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

Write it as flowing natural English describing the finished picture—not a comma-salad of tags.
Use English regardless of the source language so the image and H3 reference plans share terms.

## 2. Reference-image ordering rules

Most image models read `imageUrls` positionally (图片1, 图片2, …). When your backend supports
reference images:

- **Position 1 = art-style reference** (if you have one). Begin the prompt with an explicit
  guard so the model copies only the look:
  `Use Image 1 only for visual style; do not copy its objects or composition.`
- **Positions 2+ = subject references** — character, then props, then scene — in a fixed order.
  Reference them by number (`Image 2 defines Lin Yue's appearance; Image 3 defines the hall`).
- **Cap at ~5 references total for ordinary image models.** MiniMax-H3 Ref2VA is a deliberate
  exception: it supports up to 9 images plus video/audio references, but every asset must be
  assigned a specific role in the H3 prompt. More files are not automatically better.
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

Both inherit the same art style, character references, scene, aspect ratio, and lighting; only
the described moment differs. For MiniMax-H3 FL2VA these become Picture 1 at 0.00 seconds and
Picture 2 at the declared 4–15 second endpoint. The H3 prompt must describe the continuous path
between them rather than merely repeating the two static states.

Do not apply this endpoint rule to Ref2VA. Its reference images may show any critical visual
fact or important moment in the target video. Choose them by role—identity, costume, location,
style, prop, facial detail, decisive action, or composition—and map each to `reference_image`
without a timestamp.

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
Use Image 1 only for visual style; do not copy its objects or composition. A close-up frames
Lin Yue as his wary gaze turns to shock, his brow tightening before his eyes widen. Image 2
defines Lin Yue's appearance; remove its pure-white background and integrate him naturally into
the rainy hall. Warm amber light falls from the upper side while the background remains soft.
Keep Image 1's film grain and low-saturation warm-cool contrast.
```

### No reference-image support (features transcribed)

```text
Cinematic film texture with grain and low-saturation warm-cool contrast. A close-up frames Lin
Yue, a thirty-year-old man with short cropped hair, straight brows, an old chin scar, and a dark
trench coat. His wary gaze turns to shock as warm amber light falls from the upper side in a
rainy hall; the background remains soft.
```

### First / last frame pair (for video)

- First: `Lin Yue's hand has just touched the handle; the door is still closed.`
- Last: `The door is open and Lin Yue leans halfway into the hall as rain drips from his coat.`
