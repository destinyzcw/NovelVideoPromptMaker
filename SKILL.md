---
name: novel-to-ltx-video-prompts
description: >-
  Turn novel or story prose into shot-by-shot LTX-2.3 (LTX-2) text-to-video prompts.
  Use this whenever the user wants to adapt a book, novel, chapter, fanfic, or any
  long-form narrative text into AI video prompts, storyboard shots, or a video
  generation script — especially when they mention LTX, LTX-2, LTX-2.3, DrawThings,
  "make videos from my novel", "turn this chapter into video prompts", chunking a
  story into scenes/clips, or organizing prompts so they map back to chapters for
  review and regeneration. Trigger even if the user only says "video prompts from
  this text" or names a .txt novel file, since prose-to-video-prompt adaptation is
  exactly this skill's job.
---

# Novel → LTX-2.3 Video Prompts

Adapt long-form prose into a well-organized set of LTX-2.3 video prompts, one prompt
per short clip, laid out so every clip maps back to the exact chapter and passage it
came from. That mapping is the whole point: the user generates videos, reviews them
against the source, and regenerates individual clips without redoing everything.

**You (the agent) do the creative work** — reading each chapter, deciding where one
shot ends and the next begins, and writing cinematic prompts. **The bundled scripts do
the deterministic work** — splitting chapters, persisting output in a consistent
layout, and validating it. Don't reimplement the scripts by hand.

## Before you start

1. **Read `references/ltx2-prompt-guide.md` in full.** It is the distilled rulebook for
   what makes an LTX-2.3 prompt good (single chronological paragraph, element ordering,
   the mandatory audio layer, negative prompts, failure modes). Every prompt you write
   must follow it.
   - For the *why* behind these rules plus accurate model facts, failure-mode fixes, and
     the CJK lip-sync caveat, consult `references/ltx2-usage-notes.md` (deep-research
     findings from Lightricks' own docs/system-prompts and field-tested community sources).
2. Confirm the input with the user if unclear: the path to the novel `.txt`, where to
   write output, and roughly how long each clip should be (default ~5 s / 121 frames).

## Workflow

### Step 1 — Split the novel into chapters

Run the splitter. It parses chapter markers and scaffolds **one flat JSON file per
chapter** (`chapter-NNN-<slug>.json`) that carries the verbatim chapter text in its
`source_text` field — no per-chapter folders, no separate `source.txt`.

```
python scripts/split_chapters.py "PATH/TO/novel.txt" --out "PATH/TO/output"
```

If the novel uses unusual chapter markers, pass `--regex`. If it has no markers, the
whole file becomes one chapter — that's fine. The command prints the project path and
each chapter file's path, and writes `manifest.json` (your index + status tracker, which
records each chapter's `file`).

### Step 2 — Read the whole chapter and plan it as a unit (this is your job)

Read the chapter file's `source_text` **in full first**, and plan the chapter as a whole before
writing any prompt. Generating all of a chapter's scenes together — rather than chunking
the text and prompting each fragment in isolation — is what keeps the clips consistent:
the same character looks the same in every shot, the setting stays coherent, and the
scene order reads as one continuous sequence. Produce two things from this read:

**(a) A cast sheet.** List the characters who appear, each with a *fixed, concrete visual
description* — age, build, hair, clothing, distinguishing details (`Mira — woman in her
20s, dark hair tied back, patched red wool cloak, heavy canvas pack, dented brass lantern`).
Locking these down once is what prevents a character's face or outfit from drifting between
clips. You pass this to the writer as a `characters` array, and it is remembered
project-wide (`characters.json`) so later chapters stay consistent too. **Each scene is
generated as a separate clip and the model has no memory across clips**, so this look must
be re-stated in every prompt the character appears in — the cast sheet is what keeps those
restatements identical (see the reuse rule in Step 3).

**(b) A scene breakdown.** Segment the chapter into scenes. A **scene = one LTX-2.3 clip =
one continuous, filmable action** (roughly 3–10 seconds). Judgment matters more than any
fixed rule:

- **Cut on change.** Start a new scene when the location, time, point-of-view subject,
  or core action changes.
- **One clear action per clip.** LTX-2.3 renders singular grounded motion well and
  mangles overlapping or rapid-fire action. Three distinct beats (she stands, crosses the
  room, throws open the window) are often three scenes.
- **Prefer depictable moments.** Turn *visible* beats into scenes; compress internal
  monologue, or translate it into a visible cue.
- **Don't over-fragment.** A dense chapter might yield 6–15 scenes, a quiet one 2–4. Aim
  for the meaningful visual beats, not one clip per sentence.
- **Plan continuity across the set.** Because you're designing all scenes together, keep a
  consistent camera language and lighting arc across the chapter, and carry recurring
  props/settings from scene to scene.

For each scene, capture the **`source_excerpt`**: the verbatim (or lightly trimmed) span
of chapter text the clip depicts. This is what lets the user map a video back to the
novel, so keep it faithful — copy real phrasing from the chapter's `source_text`, don't invent it.

### Step 3 — Write the LTX-2.3 prompt for each scene

Now write the prompts for the whole chapter as a set. Because each scene is rendered as an
independent clip and **LTX-2.3 has no memory across clips**, a character only looks the
same from shot to shot if you give the model that anchor every time. Two levers hold a look
steady, and you use both:

1. **Restate the character's canonical anchors — worded identically — in every prompt they
   appear in.** Pull the exact trait phrases from your cast sheet (`characters.json`) and
   reuse them *verbatim*; do **not** paraphrase, reorder, or drop them shot to shot.
   Paraphrasing ("同一个青年" in place of the full look) or foregrounding different traits
   each time is exactly what makes hair, build, and clothing drift — the model re-invents
   whatever you leave unstated.
2. **Chain continuous runs through DrawThings' image-to-video carry-over.** For a scene you
   mark `continuation: true`, DrawThings renders it starting from the previous clip's *last
   frame* (its native "use last frame" / I2V), so the character's look is inherited pixel-
   for-pixel. On those carried clips you can keep the restated anchors light; on a **fresh**
   T2V clip (new scene, no carried frame) the text is the only anchor, so restate the full
   canonical look there.

Following `references/ltx2-prompt-guide.md`, each prompt is a single chronological paragraph
(4–8 sentences, under 200 words) ordering elements as: main action → gestures →
appearance → environment → camera → lighting/color → scene shift → dialogue, **with the
sound for each beat woven in next to that beat** (not saved for the end — see the audio rule
below).

**Imagine the shot, don't transcribe the prose.** After reading the chapter, picture how
this beat would actually play on screen and write *that* down — do not paraphrase the
novel's narration. Before writing, **read `references/ltx2-official-examples.md`** — it
holds all 11 verbatim prompt examples from the LTX-2 team, the LTX-2 team's verbatim
golden-rule guidance, and a **derived authoring checklist**. Pattern-match against the
examples and satisfy every checklist item rather than inventing a house style. The camera
is the protagonist of the description: author it as camera choreography, following the
LTX-2 team's own camera guidance (see the "Camera language" section of the guide):

- **Vary your opening — don't reuse one template.** The official examples open in five
  different ways (slug line `INT./EXT. … – DAY`, location-first, action-first,
  subject-first, "The camera opens…"). Never start every scene with the same stock phrase
  like "Cinematic medium shot, slow dolly-in" — pick the opening that fits *this* beat.
- **Chain the camera through the shot (camera A → change → camera B → …).** A prompt is
  not `<one camera label> + a paragraph`. Like the monster-truck and "we need to run"
  examples, give the camera **2–4 distinct moves within the single shot**, each triggered
  by an action beat: e.g. *toward camera → pans left to follow → handheld tracks away →
  returns until extreme close-up*. Use the subject's action as the hinge that motivates
  each next move.
- **Motivate each move and end on a defined framing.** A move should *do* something —
  reveal a new subject (pan right to reveal…), change the relationship (dolly back until a
  second figure enters in an over-the-shoulder), or land a beat (push in on her face).
  Name the end state ("…until seen in extreme close-up", "…until she fills the frame").
- **Match detail to shot scale** — close-ups need more facial/gesture precision than
  wide shots. Use present tense throughout, and vary framing/angle across a chapter's
  scenes so the sequence feels edited, not cloned.

**Before saving each scene, check it against the "Derived authoring checklist" in
`ltx2-official-examples.md`.** The rules the drafts most often break — enforce them:

- **Show emotion, never label it.** No bare "sad / angry / nervous / determined"; render
  it as posture, gesture, and expression ("jaw tight", "shoulders hunched", "eyes
  darting").
- **No on-screen text, signage, logos, or brand names** — LTX-2 can't render readable
  text, so keep them out (and in the negative prompt).
- **One subject, one primary action per clip.** Don't overload the shot with crowds,
  simultaneous layered actions, or excessive objects; it reduces accuracy. Split a busy
  beat into two scenes instead.
- **Keep lighting logic consistent** — one motivated light scheme per shot; don't mix
  conflicting sources unless the scene clearly justifies it.
- **Avoid chaotic/non-linear physics** (jumping, juggling, fast twisting) that glitches;
  prefer smooth, motivated motion.
- **Use restrained, concrete language.** LTX-2.3's own prompt enhancer strips empty
  intensifiers — prefer `red dress` over `vibrant red`, `soft side-light` over `blinding
  glow`. Named appearance and motion carry the shot; adjectives like *epic/dynamic/
  stunning* do not. (A single light style cue at the open is fine; don't pile them up.)
- **Visual and audio only — no smell, taste, or touch.** Render "cold" as breath fogging
  or a shiver, not "the icy air stings her skin".
- **Block the scene spatially.** State left/right, foreground/background, facing, and
  distance between subjects so the model has a stage, not just a description.
- **Match prompt density to duration.** A short prompt on a long clip makes the model
  rush; scale the number of concrete beats to the clip length (4–8 sentences for ~5 s).
- **Motivate every camera move; don't stack contradictory cues** (no "handheld + smooth
  gimbal"). Plain "static camera" text is unreliable — if you need a locked frame, write
  "tripod locked, no camera movement".
- **CJK dialogue caveat.** Native-language speech is correct, but lip-sync is only
  validated for EN/FR/ES/DE/RU. For Chinese/Japanese talking beats keep lines short and
  favor close-up framing so delivery reads clearly.

Every prompt must include 3–5 layered sound cues (ambient + action + accent) because
LTX-2.3 generates audio in the same pass. **Thread each sound into the sentence describing
the beat it accompanies — spread the soundscape *through* the paragraph, and never dump all
the sounds in one trailing bracket at the very end.** A trailing catch-all group (e.g. a
final `【山风…、脚步、鸦啼、呼吸】` tacked on after the action) is a known failure mode: the
model largely ignores it, which is why ambient audio dumped there doesn't make it into the
video. Instead attach the wind to the moment the wind blows, the footsteps to the step, the
accent sound to its beat, so audio intensity rises and falls with the action. You may still
use a short inline `[sound, sound]` / `【声, 声】` group *beside its beat* mid-paragraph, but
never a mechanical `Audio:` / `音效：` label and never leak layer names ("as accent") into
the prompt. In dialogue-heavy scenes that could attract stray music (cafés, parties), anchor
the acoustic explicitly — "close-mic speech, quiet room tone, no background music" — since
negative prompts don't reliably remove it. Convert stated emotions into visible cues. Keep
on-screen text, logos, and frantic motion out.

**Spoken dialogue — aim for a line in every scene you can.** Videos are far more alive
when characters speak, so treat dialogue as the default, not the exception: **give every
scene a spoken line unless it's genuinely impossible or would feel forced** (pure scenery
with no character on screen, or a silent beat where a line would break the moment). Source
the lines in priority order:

1. **Quoted speech in the prose** — use the character's actual words verbatim.
2. **Implied or reported speech** — if the novel says a character agreed, pleaded, or
   greeted someone, render it as a short natural spoken line consistent with the text.
3. **A faithful invented line** — for a character alone or acting silently, a natural
   muttered, whispered, or spoken line that fits their situation (a breathed "Just a
   little further…", a quiet name, a curse under the breath) is welcome. Favor a real,
   complete line over a single clipped word — fuller dialogue reads better on screen —
   but keep it in character and true to the scene; never invent plot or contradict the
   novel.

LTX-2.3 takes a **single prompt and has no separate transcript input** — a line is only
voiced/lip-synced if it appears, in quotation marks, **inside the scene prompt itself**.
So embed each spoken line verbatim in the prompt, name the speaker and their mouth action
so sync lands, keep one speaker per clip, and keep the line short enough to fit (~2–3
English words or ~5 CJK characters per second). Write the whole prompt — including
dialogue — in the **novel's own language** (Chinese novel → Chinese prompt, Japanese →
Japanese). Also record the same line in the scene's structured `dialogue` array (below);
this array is **internal metadata in the chapter JSON, not model input** — `save_scenes.py`
uses it only to check the line fits the clip, to report **dialogue coverage** (how many
scenes have a spoken line; aim to keep it high), and — as a safety net — to auto-weave any
line you forgot to embed. LTX-2.3 voices the line **solely from inside the prompt**; the
prompt is the single source of speech.

**Maintain continuity across clips.** Each clip is generated independently, so a character's
key visual look must be restated in **every** prompt they appear in — pulling the anchors
from your cast sheet and keeping them **verbatim** (same trait words, same order). Reusing
the identical anchor phrases is the point: it's what stops the face, build, and clothing
drifting between shots. The failure to avoid is *paraphrasing or thinning* the description —
writing "同一个青年阿泽" or foregrounding only one trait leaves the rest for the model to
re-invent, and it will (different hairstyle, different cloak, next clip). Weave the anchors
into the action naturally, but don't alter the load-bearing words: age/build, hair, signature
garment, signature prop appear the same way each time. Only for a `continuation` clip that
DrawThings starts from the previous clip's last frame (below) is the look already fixed by
the carried frame, so there you can restate lightly. The canonical full description lives in
`characters.json` for the human and for regeneration. Reuse the same names and looks in later
chapters.

**Match the novel's language.** Write the whole scene prompt in the **same language as
the source novel** — a Chinese novel gets Chinese prompts, a Japanese novel gets Japanese
prompts, an English novel gets English prompts. Keep the LTX-2.3 element ordering and the
mandatory audio layer regardless of language; only the words change. (LTX-2.3 does not
document a required prompt language, and matching the source keeps voice, tone, and
cultural detail consistent. If you ever find adherence weak on a specific shot, an English
rewrite of that one prompt is a reasonable fallback to test — but native-language is the
default.)

**Chaining long sequences — let DrawThings carry the last frame.** LTX-2.3 caps one
generation at ~10–20 s, so a continuous stretch of story (a single unbroken action, a
conversation, a walk) must be rendered as several short clips. A cut between two clips is
only invisible if the second clip *starts* exactly where the first *ended*. **DrawThings does
this for you**: it can take the last frame of a rendered clip and use it as the start image
(image-to-video) for the next clip, so the skill no longer extracts frames itself. Your job
is only to mark and phrase the continuation correctly:

- **Only chain clips that are truly continuous.** A hard cut to a new location/time is a
  fresh scene, not a continuation — don't chain those (a clean cut is fine there).
- **Give an `end_state` to every clip that feeds a continuation** — one concrete line
  describing its final frame: subject position, framing/shot scale, pose, and lighting
  (`阿泽站在山口石阶上，背对来路，马灯亮着，白雾淹没身后石阶`). This is both what the next
  prompt opens from and the cue that tells the model how to *finish* the feeding clip.
- **Mark the continuing clip `continuation: true`** and **open its prompt from that frozen
  state, then describe the onward motion** — don't re-establish the whole scene. Start with
  the matching framing/pose ("紧接上一镜，同一低角度机位，他迈步越过镜头…") so the motion
  flows out of the held last frame. Because DrawThings carries that frame, the character look
  is already fixed, so keep the restated anchors light here.
- **Keep the boundary calm.** A clip that feeds another should end on settled, low-motion
  action (a held pose, a slow move); final frames mid-fast-action are motion-blurred and make
  poor start frames. Match FPS/resolution across chained clips so the seam is smooth. In
  DrawThings, render the run in order and start each continuation scene from the previous
  clip's last frame.

### Step 4 — Save the chapter's scenes

Persist the whole chapter at once with the writer script. Pass an object with the
chapter's `characters` (your cast sheet) and its `scenes` array. Each scene element:
`title`, `source_excerpt`, `prompt`, `negative_prompt` (**you author this per scene** —
see below), optional
`suggested_duration_seconds` (default 6), optional
`continuation` (`true` if this clip continues from the previous clip's last frame) and
`end_state` (a one-line description of this clip's final frame, for any clip that feeds a
continuation), and optional `dialogue` — an array of `{"speaker": "...", "line": "..."}`
for the spoken lines. Put the same quoted line inside `prompt` too; `dialogue` is internal
metadata that drives the fit checks and coverage report only.

**Author a scene-specific `negative_prompt`, in the scene's own language.** Write it
yourself — the script does **not** translate. Two rules:

1. **Match the prompt's language.** A Chinese prompt gets a Chinese negative, a Japanese
   prompt a Japanese one, an English prompt an English one. LTX-2 ships localized
   negatives, and a mismatched-language negative confuses the encoder.
2. **Tailor it to the scene.** Keep a small shared core (on-screen text, subtitles,
   watermark, warped hands, extra fingers/people) and then add what would plausibly go
   wrong *for this shot*: e.g. `bright sunlight` for a night scene, `calm still water` for
   a rapids scene, `intact modern bridge` for a ruined-bridge scene. Don't paste the same
   negative onto every scene.

If you omit `negative_prompt`, `save_scenes.py` supplies a generic **English** fallback for
an English prompt only; for a CJK prompt it leaves the negative empty and both
`save_scenes.py` and `validate.py` warn you to author a localized one. Supplying an English
negative on a CJK prompt also raises a warning.

```json
{
  "characters": [
    {"name": "Mira", "description": "woman in her 20s, dark hair tied back, patched red wool cloak, dented brass lantern"}
  ],
  "scenes": [
    {"title": "...", "source_excerpt": "...", "prompt": "...", "end_state": "final-frame framing/pose/lighting", "dialogue": [{"speaker": "Mira", "line": "..."}]},
    {"title": "...", "source_excerpt": "...", "prompt": "continues from the same framing...", "continuation": true, "dialogue": [{"speaker": "Mira", "line": "..."}]}
  ]
}
```

Write this to a temp file and pass it in (robust for large batches and non-ASCII):

```
python scripts/save_scenes.py --project "PATH/TO/output/<novel-slug>" --chapter 1 --scenes scenes.json
```

The script fills the chapter's flat **`chapter-NNN-<slug>.json`** file in place: it keeps
`source_text` and chapter metadata, and adds the `characters` cast and the fully-processed
`scenes` array (each scene's positive prompt, localized negative, duration, and continuity
fields). This single file is both the deliverable you read prompts from **and** the
machine-readable record that `validate.py` and regeneration use. It flips that chapter's
status to `generated` in the manifest and overwrites the previous scenes, so re-running it
is how you **regenerate** a chapter after edits.

Repeat Steps 2–4 for each chapter. For a large novel, work chapter by chapter and report
progress rather than trying to hold the whole book in context at once.

### Step 5 — Validate

```
python scripts/validate.py --project "PATH/TO/output/<novel-slug>"
```

This flags empty/over-long prompts, missing audio or negative prompts, out-of-range
durations, characters named without their canonical look restated (appearance-drift guard),
`source_excerpt`s that don't actually map back to the chapter text, and continuity gaps (a
`continuation` scene whose predecessor has no `end_state`). Fix anything it reports (rewrite
the scene, re-run `save_scenes.py`), then re-validate.

### Step 6 — Render the clips (optional automated path)

Once a project validates, you can turn every scene's prompt into an actual LTX-2.3 video
clip — audio and spoken dialogue included — with `render_videos.py`, which drives the
**Draw Things CLI** (`draw-things-cli generate`):

```
python scripts/render_videos.py --project "PATH/TO/output/<novel-slug>" \
    --model <ltx-2-checkpoint.ckpt> [--dry-run]
```

- Requires `draw-things-cli` (and `ffmpeg` if you want continuation chaining) on the
  machine where Draw Things' models live. `--dry-run` prints the exact commands first.
- Writes `output/<novel-slug>/videos/chNNN-sceneMM.mp4` plus a `render-manifest.json`.
  Frames are derived from each scene's `suggested_duration_seconds` at ~24 fps and snapped
  to LTX-2.3's required `8k+1` count; it skips clips already rendered (`--overwrite` to redo).
- **Why the CLI and not the HTTP API:** Draw Things' HTTP API returns only image frames
  (no audio track), which would silently drop every spoken line — so this skill renders via
  the CLI, which muxes the model's synchronized audio into a real video file.

**Continuation chaining is automatic here:** for each `continuation: true` scene, the script
extracts the previous clip's **last frame** (via ffmpeg) and feeds it to the CLI as the
image-to-video start image, carrying the character's look across the seam. After rendering,
concatenate the clips (a short cross-fade hides micro-differences); lay one continuous audio
track over a stitched multi-clip run if per-clip audio doesn't line up.

**Manual alternative (Draw Things app UI):** paste each scene's prompt into DrawThings and
render the chapter's clips **in order**; for each continuation scene use the previous clip's
last frame as its start image (DrawThings' native "use last frame" image-to-video option).
The `continuation` flag marks which scenes to chain and each feeding scene's `end_state`
describes the frame being carried.

## Output layout (what the user gets)

```
output/<novel-slug>/
├── manifest.json                        # index: chapters, scene counts, status, params
├── characters.json                      # project-wide cast sheet (fixed looks, reused across chapters)
├── chapter-001-<slug>.json              # ← one flat file per chapter: source_text + cast +
│                                        #   every scene's prompt, localized negative, duration,
│                                        #   dialogue metadata, and continuity fields
└── chapter-002-<slug>.json
```

## Regenerating individual clips

Because everything is addressable by **chapter number + scene index** and each scene
stores its `source_excerpt`, targeted regeneration is easy:

- The user says "chapter 3, scene 2 looks wrong." Read that chapter's JSON file and
  its `source_excerpt`, rewrite just that scene's prompt, and re-run `save_scenes.py` for
  the whole chapter (pass the full updated array so indices stay stable).
- To retune every clip in a chapter (e.g. shift to night, or a more handheld camera
  style), regenerate that chapter's scenes with the adjustment applied consistently.

## Handoff

When done, tell the user the project path, how many chapters/scenes were generated, any
validation warnings, and that each chapter's `chapter-NNN-<slug>.json` holds every scene's
prompt and localized negative ready to paste into DrawThings (rendering `continuation`
scenes from the previous clip's last frame). Recommend they review a few clips first, then
batch the rest.
