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
2. Confirm the input with the user if unclear: the path to the novel `.txt`, where to
   write output, and roughly how long each clip should be (default ~6 s).

## Workflow

### Step 1 — Split the novel into chapters

Run the splitter. It parses chapter markers and scaffolds one folder per chapter with
the verbatim `source.txt` you'll read.

```
python scripts/split_chapters.py "PATH/TO/novel.txt" --out "PATH/TO/output"
```

If the novel uses unusual chapter markers, pass `--regex`. If it has no markers, the
whole file becomes one chapter — that's fine. The command prints the project path and
each chapter's `source.txt` location, and writes `manifest.json` (your index + status
tracker).

### Step 2 — Read the whole chapter and plan it as a unit (this is your job)

Read the chapter's `source.txt` **in full first**, and plan the chapter as a whole before
writing any prompt. Generating all of a chapter's scenes together — rather than chunking
the text and prompting each fragment in isolation — is what keeps the clips consistent:
the same character looks the same in every shot, the setting stays coherent, and the
scene order reads as one continuous sequence. Produce two things from this read:

**(a) A cast sheet.** List the characters who appear, each with a *fixed, concrete visual
description* you will reuse verbatim in every scene they're in — age, build, hair, clothing,
distinguishing details (`Mira — woman in her 20s, dark hair tied back, patched red wool
cloak, heavy canvas pack, dented brass lantern`). Locking these down once is what prevents
a character's face or outfit from drifting between clips. You pass this to the writer as a
`characters` array, and it is remembered project-wide so later chapters stay consistent too.

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
novel, so keep it faithful — copy real phrasing from `source.txt`, don't invent it.

### Step 3 — Write the LTX-2.3 prompt for each scene

Now write the prompts for the whole chapter as a set, pulling character descriptions from
your cast sheet so they read identically across clips. Following
`references/ltx2-prompt-guide.md`, each prompt is a single chronological paragraph
(4–8 sentences, under 200 words) ordering elements as: main action → gestures →
appearance → environment → camera → lighting/color → scene shift → audio & dialogue.

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

Every prompt must include 3–5 layered sound cues (ambient + action + accent) because
LTX-2.3 generates audio in the same pass, but **weave the sounds into the sentences or a
`[sound, sound, sound]` bracket group — never a literal `Audio:` / `音效：` label, and
never leak layer names like "as accent" into the prompt.** Convert stated emotions into
visible cues. Keep on-screen text, logos, and frantic motion out.

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
`save_scenes.py` uses it to build the human-facing transcript, to check the line fits the
clip, and — as a safety net — to auto-weave any line you forgot to embed. It also reports
**dialogue coverage** (how many scenes have a spoken line); aim to keep that high. The
`transcript.txt` it produces is a reference/subtitle copy for review, **not** model input.

Maintain **continuity across clips** using your cast sheet: paste each character's fixed
description into every scene they appear in, so their face, build, and clothing stay
identical from shot to shot. The writer also stores the cast in a project-wide
`characters.json`, so reuse the same names and descriptions in later chapters.

**Match the novel's language.** Write the whole scene prompt in the **same language as
the source novel** — a Chinese novel gets Chinese prompts, a Japanese novel gets Japanese
prompts, an English novel gets English prompts. Keep the LTX-2.3 element ordering and the
mandatory audio layer regardless of language; only the words change. (LTX-2.3 does not
document a required prompt language, and matching the source keeps voice, tone, and
cultural detail consistent. If you ever find adherence weak on a specific shot, an English
rewrite of that one prompt is a reasonable fallback to test — but native-language is the
default.)

### Step 4 — Save the chapter's scenes

Persist the whole chapter at once with the writer script. Pass an object with the
chapter's `characters` (your cast sheet) and its `scenes` array. Each scene element:
`title`, `source_excerpt`, `prompt`, optional `negative_prompt` (a sensible default is
applied if omitted), optional `suggested_duration_seconds` (default 6), and optional
`dialogue` — an array of `{"speaker": "...", "line": "..."}` for the spoken lines. Put the
same quoted line inside `prompt` too; `dialogue` drives the transcript and the fit checks.

```json
{
  "characters": [
    {"name": "Mira", "description": "woman in her 20s, dark hair tied back, patched red wool cloak, dented brass lantern"}
  ],
  "scenes": [
    {"title": "...", "source_excerpt": "...", "prompt": "...", "dialogue": [{"speaker": "Mira", "line": "..."}]}
  ]
}
```

Write this to a temp file and pass it in (robust for large batches and non-ASCII):

```
python scripts/save_scenes.py --project "PATH/TO/output/<novel-slug>" --chapter 1 --scenes scenes.json
```

The script writes `scene-01.txt` (ready to paste into DrawThings), `scene-01.negative.txt`,
a canonical `scenes.json` per chapter, and — if any scene has dialogue — a
`transcript.txt` listing every spoken line by scene and speaker. It flips that chapter's
status to `generated` in the manifest, and clears old `scene-*.txt` first, so re-running
it is how you **regenerate** a chapter after edits.

Repeat Steps 2–4 for each chapter. For a large novel, work chapter by chapter and report
progress rather than trying to hold the whole book in context at once.

### Step 5 — Validate

```
python scripts/validate.py --project "PATH/TO/output/<novel-slug>"
```

This flags empty/over-long prompts, missing audio or negative prompts, out-of-range
durations, and — importantly — `source_excerpt`s that don't actually map back to the
chapter text. Fix anything it reports (rewrite the scene, re-run `save_scenes.py`), then
re-validate.

## Output layout (what the user gets)

```
output/<novel-slug>/
├── manifest.json                 # index: chapters, scene counts, status, params
├── characters.json               # project-wide cast sheet (fixed looks, reused across chapters)
├── chapter-001-<slug>/
│   ├── source.txt                # verbatim chapter text
│   ├── chapter.json              # chapter metadata
│   ├── scenes.json               # canonical scenes: cast + excerpt + prompt + dialogue (edit to regenerate)
│   ├── transcript.txt            # spoken lines by scene/speaker (only if the chapter has dialogue)
│   ├── scene-01.txt              # positive prompt, paste-ready (spoken lines quoted inside)
│   ├── scene-01.negative.txt     # negative prompt
│   └── scene-02.txt ...
└── chapter-002-<slug>/ ...
```

## Regenerating individual clips

Because everything is addressable by **chapter number + scene index** and each scene
stores its `source_excerpt`, targeted regeneration is easy:

- The user says "chapter 3, scene 2 looks wrong." Read that chapter's `scenes.json` and
  its `source_excerpt`, rewrite just that scene's prompt, and re-run `save_scenes.py` for
  the whole chapter (pass the full updated array so indices stay stable).
- To retune every clip in a chapter (e.g. shift to night, or a more handheld camera
  style), regenerate that chapter's scenes with the adjustment applied consistently.

## Handoff

When done, tell the user the project path, how many chapters/scenes were generated, any
validation warnings, and that each `scene-NN.txt` is ready to paste into DrawThings with
its matching `.negative.txt`. Recommend they review a few clips first, then batch the rest.
