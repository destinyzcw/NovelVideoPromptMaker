---
name: storyboard-prompt
description: >-
  Convert a screenplay scene (剧本/场次) into a professional shot list (分镜脚本),
  storyboard-frame prompts, and MiniMax-H3-native audiovisual prompts. Use whenever
  the user wants to break a scene into shots, design 分镜 / storyboard, decide
  景别/运镜/机位, write storyboard image prompts, or prepare MiniMax-H3 T2VA, I2VA,
  FL2VA, or Ref2VA generation prompts. Trigger on "拆分镜", "写分镜", "generate
  storyboard prompts", "给这场戏做分镜图", "把剧本变成分镜", "MiniMax-H3",
  "Hailuo-03", "H3 video prompt", "首尾帧生成视频", "参考图生成视频", or requests
  to preserve screenplay dialogue, VO, ambience, sound effects, music, character
  identity, style, motion, camera, or voice references in generated video. The
  default image backend is Z-Image Turbo; the default video backend is MiniMax-H3.
  This is the second stage after screenplay-writer and authors prompts only.
---

# Storyboard Prompt Generator (MiniMax-H3)

Turn a screenplay scene into:

1. a director-readable shot list;
2. storyboard keyframe prompts for Z-Image Turbo or another image backend;
3. one production-ready MiniMax-H3 audiovisual prompt package per shot.

Read `references/minimax-h3-video.md` before writing H3 prompts. It is derived from MiniMax's
official Base and Full-Reference prompt guides and defines the exact field order, dialogue
syntax, speaker IDs, reference labels, and mode constraints.

## Backend roles

- **Storyboard stills — Z-Image Turbo by default.** Read `references/z-image-turbo.md`.
  It is text-to-image, ignores negative prompts at CFG≈0, and benefits from long natural
  language plus verbatim identity anchors.
- **Audiovisual video — MiniMax-H3 by default.** It generates video and 32-kHz stereo audio
  together at 24 fps. Each output lasts an integer 4–15 seconds.
- The skill writes prompts and request plans; it does not invoke either backend.

## Establish the visual and audio bible

Before splitting shots, record:

- **Style phrase** — one invariant sentence describing medium, palette, lighting texture,
  rendering style, and overall visual treatment.
- **Visual anchors** — one canonical physical description for every recurring character,
  location, and important prop. Reuse each phrase verbatim in storyboard-image prompts.
- **Speaker registry** — assign `(S1)`, `(S2)`, and so on in order of first vocal event in
  the scene. A speaker keeps the same ID across all shots. VO and OS reuse that character's ID.
- **Voice intent** — age range, pitch, timbre, pace, accent, and delivery only when the
  screenplay or reference assets establish them. Do not invent a celebrity voice.
- **Sound palette** — persistent ambience, recurring physical sounds, and audience-only score.
- **Reference inventory** — available character/style/scene images, motion/camera videos, and
  voice/music audio. Record the purpose of each asset rather than merely listing filenames.

## Pass 1 — Design H3-feasible shots

Let the drama choose coverage:

- dialogue: shot/reverse-shot, reaction shots, medium and close framing;
- action: tracking, handheld, fast cuts, clear cause→effect;
- emotion: close-up plus slow push-in and room for the post-line reaction;
- scene change: a real cut or transition, not an impossible movement inside one FL2VA shot.

Each H3 generation must be **4–15 seconds**. Prefer **4–8 seconds per shot** for reliability.
Use one continuous camera setup per FL2VA shot. If a beat needs a large viewpoint change, a
different location, or several unrelated actions, split it into separate shots instead of
building a chain of 2-second interpolation clips.

For every shot decide:

- 景别, duration, camera motion, angle, composition;
- visible action path: opening state → observable intermediate changes → ending state;
- dialogue/VO/OS and the exact vocal source;
- ambient sound, synchronized SFX, and audience-only music;
- visual anchors and reference assets;
- H3 mode.

### Complexity budget

Aim for one primary action, one camera movement, and one active speaker per shot. H3 can handle
more, but retries rise when a short clip combines multiple speakers, major physical action,
large camera travel, dense text, and several sound events.

Do not shorten dialogue, translate it, or silently move it to another shot to satisfy the
budget. Split the shot at a natural dramatic boundary.

## Pass 2 — Choose the H3 mode

Choose exactly one mode per generation request.

### FL2VA — default for storyboard-controlled shots

Use first-and-last-frame generation when exact opening and closing composition matter.

- `Picture 1` is the first frame at `0.00`.
- `Picture 2` is the last frame at the shot duration.
- Write the continuous physical and camera path connecting them.
- Usually keep one `[Shot 1]` with no internal cuts.
- The two frames should describe compatible identity, environment, lighting, and viewpoint.

FL2VA is the normal replacement for the former LTX workflow. A shot normally gets **K0 and K1,
one H3 prompt, and one 4–15 second video**, not several 2–4 second clips. Add an intermediate
storyboard frame only as planning evidence or split the action into a new shot; H3's API accepts
only one first frame and one last frame per request.

### I2VA or L2VA

Use I2VA when only the opening composition must be exact, and L2VA when only the landing frame
must be exact. Let the model develop or infer the unconstrained side of the timeline.

### T2VA

Use text-only generation for establishing shots, effects, inserts, or transitions where strict
character identity and exact endpoint composition are not required.

### Ref2VA — use references instead of first/last frames

Use reference mode when character identity, location, style, motion, camera movement, voice
timbre, music, or another reusable attribute matters more than exact endpoint frames.

- Up to 9 reference images, 3 reference videos, and 3 reference audios; at most 12 files.
- Audio cannot be the sole reference input.
- Assign every reference a specific job.
- Use `<Subject N>`, `<Picture N>`, `<Video N>`, and `<Audio N>` consistently.
- Produce `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`,
  `overall_soundscape`, and `non_diegetic_music`, all in English except original dialogue,
  lyrics, and visible text.

**API boundary:** reference inputs and first/last-frame inputs are mutually exclusive. Never
emit a request that mixes `reference_image/reference_video/reference_audio` with
`first_frame/last_frame`.

## Pass 3 — Compose storyboard image prompts

For each required keyframe, follow `references/z-image-turbo.md`:

- write one complete natural-language paragraph;
- group each subject's appearance, position, action, and expression together;
- reuse visual anchors verbatim;
- state lighting separately;
- end with positive cleanliness constraints;
- place sampler parameters outside the prompt code block.

For FL2VA, author:

- **K0 / Picture 1:** the precise opening state;
- **K1 / Picture 2:** the precise ending state;
- optional planning frames between them, clearly marked **not API inputs**.

K0 and K1 must preserve character identity, clothing, location, style, aspect ratio, and
lighting unless the screenplay explicitly changes them. Unlike the former LTX workflow, matching
seeds are a useful storyboard-generation tactic but are not an H3 API requirement.

## Pass 4 — Compose the H3 prompt

H3 prompt structure is strict. Use English for prompt prose because the official Context-IR
formats are English. Keep dialogue and visible text in their original language.

### Base modes: T2VA / I2VA / FL2VA / L2VA

Use the mode-specific alignment instruction from `references/minimax-h3-video.md`, then exactly:

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

In `integrated_multimodal_description`:

- establish style, composition, subjects, position, and opening state;
- describe camera motion as type + meaningful amplitude + speed;
- choreograph visible actions and reactions in playback order;
- keep stable speaker IDs across shots;
- derive the language tag from the source and format speech as
  `<d>[Language] exact original dialogue.</d>`; for example, use `[Chinese]` only for Chinese;
- for VO, write `says in an off-screen voiceover` and state that the visible character's
  lips remain completely closed;
- place synchronized diegetic sounds where they occur;
- use timestamped `[Shot N]` only for real internal cuts in T2VA/Ref2VA, not minor reframing.

`overall_soundscape` is 1–4 English sentences covering ambience, physical action sounds, and
non-verbal human sounds. Do not repeat dialogue.

`non_diegetic_music` is 1–3 English sentences describing audience-only instrumentation, tempo,
rhythm, and dynamics. Use `N/A` when no score is wanted.

### Ref2VA

Follow the six-section schema in `references/minimax-h3-video.md`. Make the relationship between
each reference and the target explicit:

- identity, costume, prop, or environment → `<Subject N>`;
- concrete storyboard/keyframe planning anchor → `<Picture N>`;
- source edit, continuation, motion, cuts, rhythm → `<Video N>`;
- copied or referenced voice/music/sound → `<Audio N>`.

Use only the official retention markers. Do not promise full preservation when the user asks for
a substantial attribute change.

## Output format

Produce Markdown with a scene header, bible, shot table, then one block per shot.

````markdown
## 分镜：第 {集} 集 · {集数}-{场次} {地点}

**画风**：{style phrase}
**视觉锚点**：{entity → invariant anchor}
**说话人**：{角色 → S1/S2... + voice intent}
**参考素材**：{asset → identity/style/motion/camera/voice/music role}

| 镜号 | 时长 | 景别/机位 | 运镜 | 起点→过程→落点 | 台词/VO | 声音 | H3模式 |
|---|---:|---|---|---|---|---|---|
| 01 | 6s | 中景/低角度 | 慢速小幅推近 | 迈步逼近→停住俯视 | 赵天骄：… | 崖风/碎石/低弦 | FL2VA |

### 镜号 01

**模式与请求参数**：MiniMax-H3 FL2VA｜duration=6｜resolution=2K｜ratio=adaptive

**Picture 1 / K0 首帧 — Z-Image Turbo**
```text
{complete storyboard image prompt}
```
参数：{outside prompt}

**Picture 2 / K1 尾帧 — Z-Image Turbo**
```text
{complete storyboard image prompt}
```
参数：{outside prompt}

**MiniMax-H3 FL2VA prompt**
```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 6.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

**API素材映射**：Picture 1 → `first_frame`; Picture 2 → `last_frame`.
````

For Ref2VA, replace the two endpoint-frame blocks with an ordered reference manifest and emit
the six-section Ref2VA prompt. State explicitly that no first/last-frame roles are included.

## Final checks

- Every duration is an integer from 4 through 15.
- FL2VA endpoint timestamps exactly equal the declared duration with two decimals.
- FL2VA normally contains one continuous shot and reaches Picture 2 at the end.
- Ref2VA never mixes reference roles with first/last-frame roles.
- Speaker IDs stay stable across the scene.
- Every spoken word and punctuation mark is preserved inside `<d>`.
- VO explicitly keeps visible lips closed.
- Dialogue is absent from `overall_soundscape`.
- Diegetic music stays in the timeline; audience-only score stays in `non_diegetic_music`.
- Prompt prose is English; original dialogue, lyrics, and visible text keep their source language.
- Parameters and explanatory notes remain outside prompt code blocks.

For H3 mode details and worked examples, read `references/minimax-h3-video.md`. For image
prompt composition, read `references/z-image-turbo.md`; for other image backends, read
`references/prompt-composition.md`.
