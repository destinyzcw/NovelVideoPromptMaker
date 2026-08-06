# MiniMax-H3 audiovisual prompt playbook

This reference follows MiniMax's official H3 model card and the two prompt guides published in
the MiniMax-H3 Hugging Face repository:

- `VIDEO_PROMPT_WRITING_GUIDE_base_en.md` for T2VA, I2VA, FL2VA, and L2VA
- `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` for full-reference Ref2VA

Use these schemas rather than adapting prompt habits from other video models.
Also validate request plans against MiniMax's current official API documentation:

- https://platform.minimax.io/docs/guides/video-generation
- https://platform.minimax.io/docs/guides/video-prompt
- https://platform.minimax.io/docs/api-reference/video-generation-v2-create

## 1. Capability envelope

- Output: native video plus 32-kHz stereo audio, 24 fps
- Duration: integer 4–15 seconds
- Resolution: 768P base or hosted 2K
- Ratios: 21:9, 16:9, 4:3, 1:1, 3:4, 9:16, with adaptive where allowed
- Stable dialogue languages: Arabic, Chinese, English, French, German, Italian, Japanese,
  Korean, Portuguese, Russian, and Spanish
- FL2VA inputs: zero, one, or two endpoint images
- Ref2VA inputs: up to 9 images, 3 videos, 3 audios, maximum 12 files; audio cannot stand alone

The public API treats endpoint-frame generation and reference generation as mutually exclusive.
Do not mix `first_frame` / `last_frame` with `reference_image` / `reference_video` /
`reference_audio` in one request.

## 2. Select a mode

| Mode | Use when | Main constraint |
|---|---|---|
| T2VA | Text can define the complete audiovisual shot | T2V ratio must be concrete, not adaptive |
| I2VA | The opening frame must be exact | Develop continuously forward from Picture 1 |
| FL2VA | Opening and ending compositions must be exact | Connect Picture 1 to Picture 2 continuously |
| L2VA | Only the final landing frame must be exact | Infer a plausible opening and converge on Picture 1 |
| Ref2VA | Identity, style, scene, motion, camera, voice, music, or source video drives generation | Use six-section reference schema; no endpoint-frame roles |

For storyboard production, default to Ref2VA for character-driven and narrative shots. Prefer
FL2VA only when exact opening and ending pixels are the contract. Ref2VA reference images are
ordinary visual references and may show any critical subject, setting, prop, expression,
composition, or action moment; they are not implicitly first or last frames.

## 3. Prompt language

Write every model-facing prompt field in natural English regardless of the source language.
Translate scene description, action, camera, style, reference roles, ambience, and music into
English. Preserve original language only for verbatim dialogue or lyrics inside `<d>` and text
that must visibly appear in the scene.

## 4. Base-mode prompt contract

### Alignment instruction

The alignment instruction is the first line, followed by one blank line.

I2VA:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

FL2VA:

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 8.00-second mark of the target video.
```

Replace `8.00` with the effective duration, always formatted to two decimals. If the end frame
belongs to a later internal shot, use that actual shot number, though FL2VA normally works best
as one continuous shot.

L2VA:

```text
How the reference pictures align with the target video — <Picture 1> (from [Shot 1]) aligns with the 6.00-second mark of the target video.
```

T2VA has no alignment instruction.

### Three core fields

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

Do not rename or reorder the fields.

## 5. `integrated_multimodal_description`

Write the visual and audible timeline in playback order.

### Opening

At the start of `[Shot 1]`, establish:

1. visual style;
2. shot size and initial composition;
3. subject appearance and position;
4. environment, lighting, and important props;
5. the opening action state.

For keyframe modes, derive these from the supplied frame instead of contradicting it.

### Action path

For FL2VA, do not spend the prompt repeating two static image descriptions. Describe:

`first-frame state → observable intermediate changes → progressively narrowing difference →
last-frame state`.

End by explicitly settling into the pose, spacing, camera angle, lighting, and composition of
Picture 2.

### Cuts

- `[Shot 1]` has no timestamp.
- A real later cut starts with `[Shot N] At 00:SS.mmm, the camera cuts to...`.
- Cut times must strictly increase and remain inside the duration.
- Use a cut only when it introduces a new viewpoint, state, space, subject, or time.
- Prefer camera motion for small distance or angle changes.
- FL2VA normally favors one shot; split storyboard coverage into separate H3 requests rather
  than forcing unrelated cuts between two endpoint frames.

### Camera language

Describe camera movement naturally as:

`motion type + meaningful amplitude + meaningful speed`.

Choose one movement. Alternatives such as `push or track` are unresolved instructions and must
be replaced with a single executable choice. Do not write meta direction such as `use the stated
shot plan`; put the actual camera action in the timeline.

Useful official vocabulary:

- zoom in / zoom out
- push in / pull out
- pan left / pan right
- truck left / truck right
- tilt up / tilt down
- pedestal up / pedestal down
- arc shot
- tracking shot
- static shot
- shake slightly / shake strongly
- POV
- roll clockwise / roll counterclockwise
- with small / large amplitude
- at slow / fast speed

Example:

```text
The camera pushes in with small amplitude at slow speed toward the jade slip in his hand.
```

### Speakers and dialogue

Assign stable speaker IDs in the order of actual vocal events:

```text
The white-robed young man with a cold, controlled baritone (S1) says with contempt:
<d>[Chinese] 一个废物，也配觊觎宗门功法？</d>
```

Rules:

- Keep `(S1)`, `(S2)`, etc. stable across shots.
- In Ref2VA, bind a referenced speaker with both its subject label and ID:
  `<Subject 2> (S1), Zhao Tianjiao, says...`.
- Put speaker identity, delivery, action, and voice outside `<d>`.
- Put only `[Language]` and exact spoken content inside `<d>`.
- Preserve wording and punctuation verbatim; do not translate or improve it.
- If multiple speakers vocalize together, use `(S1,S2)`.
- Do not create a collective speaker ID unless a real group subject is explicitly defined.
- If speech crosses a cut, use `<scenetrans>` and say it continues across the cut.
- If the clip ends mid-sentence, use `<cutoff>`.

Voiceover uses the official phrase and a lip guard:

```text
The injured young man (S2) says in an off-screen voiceover:
<d>[Chinese] 我不甘心……</d> while his on-screen lips remain completely closed.
```

OS dialogue keeps the same speaker ID but states that the voice comes from outside the frame.

### Visible text

Place text genuinely visible in the scene in English double quotation marks and preserve it
verbatim. Do not add blanket “no text” clauses to an H3 prompt when the scene intentionally
contains signage or labels.

### Diegetic sound

Place time-sensitive sounds beside their visible causes:

```text
His boot grinds loose gravel as his robe snaps sharply in the crosswind.
```

Dialogue, singing, instruments, radio, television, or phone music audible to characters belong
inside the timeline, not in `non_diegetic_music`.

## 6. Audio fields

### `overall_soundscape`

Write 1–4 English sentences summarizing:

- persistent ambience;
- physical action sounds;
- non-verbal human sounds.

Do not repeat dialogue, singing, or score. Use `N/A` only for explicitly requested total silence.

### `non_diegetic_music`

Write 1–3 English sentences describing audience-only:

- instrumentation;
- tempo;
- rhythm;
- dynamic changes and timing.

Avoid abstract explanations of emotion. Use `N/A` when there is no score.

## 7. FL2VA worked example

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 6.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Live-action cinematic wuxia fantasy, a medium shot begins in the position, character appearance, cold moonlight, black-rock cliff environment, and low-angle composition established by Picture 1. The camera pushes in with small amplitude at slow speed as the tall white-robed young man with a cold, controlled baritone (S1) walks through the crosswind toward the injured disciple on the ground. His boots grind loose gravel and the silver-trimmed robe snaps behind him. He slows, stops beside the disciple, lowers his gaze, and settles into the final spacing, contemptuous expression, body posture, and composition established by Picture 2. As he comes to a complete stop, the white-robed young man (S1) says with quiet contempt: <d>[Chinese] 一个废物，也配觊觎宗门功法？</d> His lips close after the final syllable while he continues looking down at the disciple.

overall_soundscape: Strong wind moves continuously across the cliff, joined by robe fabric snapping and loose gravel rolling over black rock. Footsteps approach at an even pace and stop before the dialogue begins.

non_diegetic_music: Sustained low strings at a slow tempo gradually increase in volume during the approach, then hold a quiet unresolved note under the spoken line.
```

## 8. Ref2VA six-section contract

Write all section prose in English. Preserve original language only inside `<d>` and visible text.

```text
subject_definitions:
...

summary:
...

retention_analysis:
...

detailed_description:
...

overall_soundscape:
...

non_diegetic_music:
...
```

### `subject_definitions`

- `<Subject N>`: reusable visible content—person, animal, object, location, costume, style,
  action, expression, pose, or effect.
- `<Picture N>`: a concrete frame, keyframe, edited keyframe, or storyboard composition anchor.
- `<Video N>`: source edit/continuation or whole-video motion, cuts, rhythm, and temporal structure.
- `<Audio N>`: copied or referenced voice, music, dialogue, beat, ambience, or sound texture.

Give every separately tracked item one stable label and state its source and job.

### Selecting and generating critical reference images

Use references to carry the video's most important visual facts, not to imitate a start/end-frame
workflow. First reuse suitable supplied assets, then generate missing critical images.

1. Identify what must stay recognizable: character identity and costume, location and style,
   important props, and decisive action, expression, or composition moments.
2. Choose the smallest useful set, normally 2–5 images and never more than the API limit of 9.
3. Give each image one explicit primary job. A compatible secondary job is fine, but avoid
   crowded sheets or near-duplicate timeline samples.
4. Critical in-story images may come from any point in the target video. Refer to them as
   `<Picture N>` and map each one to API role `reference_image`; do not assign timestamps.
5. In `retention_analysis`, state what each picture contributes and whether it is fully
   preserved, partially preserved, used for attribute transfer, or only weakly referenced.
6. Check the source-state ledger before assigning each image. Do not show a prop before its
   discovery, a later injury or costume state too early, or a character before arrival.
7. Generic identity portraits do not replace state-specific references when the video depends on
   a wound, pose, group geometry, readable inscription, or decisive interaction.

MiniMax's official examples explicitly assign different reference images to mood/setting/film
grain, character, product or prop design, facial detail, and ending logo. Follow that role-based
pattern: explain how each input affects the target rather than merely listing files.

### `summary`

Start with the applicable task types:

- `[keyframe completion]`
- `[reference generation]`
- `[video editing]`
- `[video continuation]`
- `[audio reuse]`
- `[audio reference]`

Combine multiple types with ` + `.

### `retention_analysis`

Visible markers:

- `fully_preserved`
- `partially_preserved`
- `attribute_transfer`
- `weak_reference`

Audio markers:

- `fully_copy`
- `partially_copy`
- `reference`
- `weak_reference`

Use one line per label and explain what is retained or changed. Do not claim
`fully_preserved` when requested attributes materially change.
Never merge two labels into one entry such as `<Picture 1> / <Subject 1>`.

### `detailed_description`

For generation tasks, MiniMax recommends roughly 350–500 English words; this project accepts
roughly 300–500 when dense verbatim dialogue leaves less room. Before `[Shot 1]`, establish the
overall style in one or two sentences. Then describe each shot in playback order with concrete
opening composition, spatial positions, lighting, one selected camera movement, observable
intermediate actions and reactions, and synchronized diegetic sounds. Do not substitute a
template, metadata recap, or unresolved camera choice. Keep the complete hosted-API prompt under
7000 characters.

Referenced speakers use both labels:

```text
<Subject 2> (S1) turns toward the doorway and says,
<d>[Chinese] 你终于来了。</d>
```

### Ref2VA example skeleton

```text
subject_definitions:
<Subject 1> is Lin Yue in <Picture 1>, a lean sixteen-year-old disciple with tied short hair, a coarse dark robe, and a thin scar over his left eyebrow.
<Subject 2> is the black-rock cliff environment in <Picture 2>, with a dead tree at the edge and deep cold fog below.
<Audio 1> is the voice-timbre reference for <Subject 1> (S1), containing a restrained young male Mandarin voice.

summary:
[reference generation + audio reference] The target video shows <Subject 1> recovering beside <Subject 2>, using <Audio 1> as the voice-timbre reference for his spoken line.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - identity, tied hair, coarse robe, eyebrow scar, and lean build are retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - black rock, dead tree, cliff edge, and cold fog are retained.
<Audio 1>: reference - its restrained young male timbre and measured delivery guide <Subject 1>'s dialogue without copying the original signal.

detailed_description:
The target video uses a cinematic wuxia-fantasy style with cold moonlight, high contrast, and restrained handheld movement.
[Shot 1] ...

overall_soundscape:
Strong cliff wind continues throughout the shot, joined by strained breathing, cloth movement, and loose gravel sliding beneath his palm.

non_diegetic_music:
Sparse low strings at a slow tempo enter after he raises his head and remain quiet beneath the dialogue.
```

## 9. Request-plan validation

Before delivering:

- duration is an integer 4–15;
- FL2VA end timestamp equals duration to two decimal places;
- I2VA/FL2VA ratio is adaptive because endpoint images determine it;
- T2VA uses a concrete supported ratio;
- FL2VA includes at most one first and one last frame;
- Ref2VA contains no endpoint-frame roles;
- every Ref2VA image has an explicit visual job and API role `reference_image`;
- references cover the critical visual facts without redundant near-duplicates;
- references match the exact source state and do not leak later discoveries or injuries;
- every named active or speaking subject has a resolvable label;
- one concrete camera movement is written directly in the timeline;
- retention analysis has one accurate decision per label;
- reference video/audio clips are 2–15 seconds and totals stay within 15 seconds;
- speaker IDs are stable;
- dialogue is verbatim inside `<d>`;
- visible VO subject has closed lips;
- prompt text is within the API's 7000-character text limit when targeting the hosted API.
