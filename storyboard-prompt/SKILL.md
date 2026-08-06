---
name: storyboard-prompt
description: >-
  Convert a screenplay scene into a strict JSON array of production-ready image
  and MiniMax-H3 audiovisual prompts. Use whenever the user asks to split a
  script into shots or video pieces, design storyboard prompts, prepare
  MiniMax-H3/Hailuo-03 T2VA, I2VA, FL2VA, L2VA, or Ref2VA inputs, preserve
  dialogue/VO/audio, or generate critical reference-image prompts. Each JSON
  object represents one approximately 5-10 second video piece and contains its
  image inputs, image-generation prompts, H3 request settings, and video prompt.
  All model-facing prose is English except verbatim dialogue, lyrics, and visible
  text. This skill authors prompts only and never invokes generation backends.
---

# Storyboard Prompt Generator (MiniMax-H3)

Convert screenplay material into a **JSON array**. Each object is one independent,
production-ready MiniMax-H3 video generation piece lasting approximately 5-10 seconds.
The same object contains every image-generation prompt needed for that piece.

Read `references/minimax-h3-video.md` before composing H3 prompts. Read
`references/z-image-turbo.md` before composing image prompts.

## Non-negotiable output contract

- Return one raw JSON array and nothing else.
- Do not wrap the JSON in Markdown fences.
- Do not add headings, explanations, notes, or trailing text.
- Emit strict JSON: double-quoted keys and strings, no comments, no trailing commas.
- Escape line breaks inside `video_prompt` as `\n`.
- Keep the field names and nesting from the schema below.
- Each array item must be self-contained enough to submit or transform into one H3 request.

## Prompt language

Write all model-facing prose in natural English regardless of source language:

- image prompts;
- reference purposes and descriptions;
- shot, action, camera, style, ambience, and music descriptions;
- every H3 prompt section.

Preserve source language only for:

- verbatim dialogue and lyrics inside `<d>[Language] ...</d>`;
- text that must visibly appear in the generated scene;
- `source_scene` and character names when retaining their original spelling is useful.

Do not translate, rewrite, shorten, or improve spoken wording.

## Internal continuity bible

Before splitting the scene, establish internally:

- one invariant English style phrase;
- one invariant English visual anchor for each recurring character, location, costume state,
  and important prop;
- stable speaker IDs `(S1)`, `(S2)`, and so on, assigned by first vocal event;
- persistent ambience and audience-only score logic;
- available image, video, and audio references;
- stable `asset_id` values for images reused across pieces.
- a source-state ledger for each piece: time of day, location, clothing, injuries, held props,
  revealed information, and who is present.

Reuse anchor wording and asset IDs verbatim across every relevant JSON object. Do not emit a
separate bible object; copy the needed continuity information into each video piece.
Never leak a later discovery, injury, costume state, prop, inscription, or character arrival into
an earlier image or video prompt.

## Pass 1 - Split into 5-10 second video pieces

Each JSON object represents one H3 generation request.

- Target **5-10 seconds** per piece.
- Combine adjacent compatible micro-beats when a piece would be shorter than 5 seconds.
- Split at a natural action, dialogue, reaction, camera, or location boundary when a piece
  would exceed 10 seconds.
- Use one primary action, one meaningful camera movement, and normally one active speaker.
- Choose one concrete camera movement. Never write alternatives such as `push or track`, and
  never replace camera direction with meta prose such as `use the stated shot plan`.
- Preserve a reaction window after important dialogue.
- Estimate spoken duration before assigning the piece duration. Dialogue plus pauses, visible
  action, and reaction must fit at a natural pace; split the piece rather than rushing speech.
- Keep each piece visually and spatially coherent.
- Never create several short objects merely to represent evenly spaced storyboard frames.

MiniMax H3 technically accepts integer durations from 4-15 seconds. Use 4 or 11-15 only when
the source cannot be represented faithfully within 5-10 seconds; prefer combining or splitting.

## Pass 2 - Choose one H3 mode

Choose exactly one mode per object.

### Ref2VA - default for narrative pieces

Use Ref2VA when identity, costume, location, style, prop design, motion, camera, voice, or music
references matter more than exact endpoint pixels.

- Reference images are not start/end frames.
- Generate or reuse the smallest useful set of critical images, normally 2-5.
- Critical images may depict any important visual fact or moment in the target video.
- Cover the needed identity/costume, location/style, prop, expression, and decisive
  action/composition information.
- Prefer targeted state and action references over generic portraits. A reusable identity image
  is insufficient when the piece depends on a new injury, revealed prop, precise group layout,
  readable inscription, or decisive pose.
- Track every named active or speaking subject with a resolvable subject/reference label.
- For crowded confrontations, use several complementary references with spatially bound
  subgroups rather than one overloaded group image.
- Map every image to `reference_image`.
- Give every reference an explicit `purpose`.
- Never assign a timestamp to a Ref2VA image.
- Never mix reference roles with `first_frame` or `last_frame`.

### FL2VA

Use only when both opening and ending pixels must be exact.

- Include exactly one `first_frame` and one `last_frame`.
- Describe a continuous, reachable action and camera path between them.
- Use K0 and K1 asset IDs or another clear stable pair.

### I2VA or L2VA

Use I2VA when only the opening frame must be exact. Use L2VA when only the ending frame must
be exact.

### T2VA

Use text-only generation for inserts, establishing shots, effects, or transitions that do not
need visual-reference consistency. Its `image_inputs` array is empty.

## Pass 3 - Compose image inputs

Every visual input belongs in `image_inputs`.

For generated images:

- set `source` to `"generate"`;
- include a stable `asset_id`;
- include the H3 label such as `"Picture 1"`;
- set `api_role` to `reference_image`, `first_frame`, or `last_frame`;
- state one clear `purpose`;
- write a complete English `prompt`;
- include image model parameters separately from the prompt.

For supplied assets:

- set `source` to `"provided"`;
- identify the asset in `source_asset`;
- set `prompt` to `null`;
- still include its H3 label, API role, and purpose.

For an image generated once and reused in later pieces:

- keep the same `asset_id`, prompt, parameters, and visual anchors;
- keep the same seed and every parameter value exactly;
- set `source` to `"reuse"`;
- use `source_asset` to point to the stable asset ID.

Image prompts should:

- describe one finished still image, not video motion;
- group each subject's appearance, position, action, and expression;
- repeat canonical visual anchors verbatim;
- specify environment, composition, and lighting;
- end with concise positive cleanliness constraints;
- remain English even when the screenplay is not English.
- match the source-state ledger for that exact piece.
- omit blanket `no text` constraints when the required image must show readable source text;
  quote the exact visible text instead.

## Pass 4 - Compose the H3 video prompt

### T2VA / I2VA / FL2VA / L2VA

Follow the official base structure:

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

Add the official first/last-frame alignment instruction before these fields when required.

### Ref2VA

Follow the official six-section structure exactly:

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

Make every `<Picture N>`, `<Subject N>`, `<Video N>`, and `<Audio N>` relationship explicit.
Use only the retention markers documented in `references/minimax-h3-video.md`.

For `retention_analysis`:

- use one line per label; never merge `<Picture N> / <Subject N>`;
- use `fully_preserved` only when the referenced attributes truly remain unchanged;
- use `partially_preserved` or `attribute_transfer` when pose, injury, lighting, time of day,
  composition, or another material attribute changes.

Write `detailed_description` as concrete playback-order direction, normally 300-500 English words
depending on dialogue density. Establish the opening composition, subject positions, lighting,
camera motion, intermediate actions and reactions, and synchronized physical sounds. Keep the
complete H3 prompt below the API limit of 7000 characters.

### Speech and sound

- Keep stable speaker IDs across all objects.
- Bind every referenced speaker with both its actual subject label and speaker ID, for example
  `<Subject 2> (S1), Zhao Tianjiao, says...`.
- For simultaneous speech, use the actual participating speaker IDs or define a real group
  subject; never invent an unbound collective speaker.
- Put only the language tag and exact spoken words inside `<d>`.
- Use `says in an off-screen voiceover` for VO and state that visible lips remain closed.
- Put synchronized physical sounds beside their visible causes.
- Keep ambience and non-verbal sounds in `overall_soundscape`.
- Keep audience-only score in `non_diegetic_music`.
- Do not repeat dialogue in soundscape fields.

## Required JSON schema

Return an array of objects with this exact shape:

```json
[
  {
    "piece_id": "2-3-01",
    "source_scene": "2-3 Soul-Breaking Cliff",
    "duration_seconds": 7,
    "h3_mode": "ref2va",
    "model": "MiniMax-H3",
    "resolution": "2K",
    "ratio": "16:9",
    "shot": {
      "size": "medium-wide",
      "angle": "eye-level side view",
      "camera_motion": "fast tracking movement with small amplitude",
      "composition": "Lin Yue on the left, Zhao Tianjiao on the right, cliff edge behind them",
      "action_path": "the palm strike lands, Lin Yue flies backward, and his back hits the dead tree"
    },
    "dialogue": [],
    "image_inputs": [
      {
        "asset_id": "lin-yue-and-zhao-cliff-r1",
        "h3_label": "Picture 1",
        "api_role": "reference_image",
        "purpose": "character identities, costumes, confrontation spacing, and cliff visual style",
        "source": "generate",
        "source_asset": null,
        "image_model": "Z-Image Turbo",
        "prompt": "A complete English still-image generation prompt.",
        "parameters": {
          "width": 1280,
          "height": 720,
          "steps": 10,
          "cfg": 0,
          "seed": 2301
        }
      }
    ],
    "video_prompt": "subject_definitions:\n...\n\nsummary:\n...\n\nretention_analysis:\n...\n\ndetailed_description:\n...\n\noverall_soundscape:\n...\n\nnon_diegetic_music:\n..."
  }
]
```

## Field rules

- `piece_id`: stable, ordered, and unique.
- `source_scene`: original scene identifier plus a concise location label.
- `duration_seconds`: integer, normally 5-10.
- `h3_mode`: lowercase `t2va`, `i2va`, `fl2va`, `l2va`, or `ref2va`.
- `model`: always `MiniMax-H3`.
- `resolution`: `768P` or `2K`; default `2K`.
- `ratio`: a supported concrete ratio, or `adaptive` where the selected mode permits it.
- `shot`: English production intent for this piece.
- `dialogue`: ordered vocal events with `speaker`, `speaker_id`, `type`, `language`, and exact
  `text`; use an empty array when there is no speech.
- `image_inputs`: all images required for this piece; use an empty array for T2VA.
- `video_prompt`: one complete English H3 prompt string with escaped newlines.

Dialogue item shape:

```json
{
  "speaker": "赵天骄",
  "speaker_id": "S1",
  "type": "dialogue",
  "language": "Chinese",
  "text": "一个废物，也配觊觎宗门功法？"
}
```

Allowed dialogue `type` values are `dialogue`, `voiceover`, `off_screen`, `singing`, and
`group`.

## Final checks

- Output is parseable JSON and the root value is an array.
- There is one object per approximately 5-10 second video piece.
- Every object contains both the video prompt and all image inputs required for that request.
- All model-facing prose is English.
- Dialogue, lyrics, and visible text remain verbatim in their source language.
- Ref2VA images use only `reference_image` and are not treated as endpoints.
- Endpoint and reference roles never coexist in one object.
- Every generated image has a complete English prompt and parameters.
- Reused assets keep the same asset ID, anchors, prompt, parameters, and seed.
- Every piece matches the source-state ledger and contains no future-information leakage.
- Every named active or speaking subject resolves to a reference/subject label.
- Every `camera_motion` names one executable movement with meaningful amplitude and speed.
- Dialogue, action, pauses, and reaction fit naturally inside the declared duration.
- Ref2VA retention analysis contains one accurate decision per label.
- Ref2VA detailed description is shot-specific playback-order direction, not a template or
  metadata restatement, and the complete video prompt is under 7000 characters.
- H3 section names and order match the selected official mode.
- Speaker IDs remain stable across the array.
- Every duration and ratio is valid for the selected H3 mode.
- No text appears before or after the JSON array.
