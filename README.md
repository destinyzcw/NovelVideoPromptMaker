# NovelVideoPromptMaker

An **agent skill** that turns novels and long-form prose into
[LTX-2.3 (LTX-2)](https://wiki.drawthings.ai/wiki/LTX-2) text-to-video prompts —
one prompt per short clip — organized so every clip maps back to the chapter and
passage it came from, for easy review and regeneration.

This is a *skill*, not a standalone pipeline: an AI agent reads it and does the
creative segmentation and prompt writing itself. The bundled scripts handle the
deterministic parts (splitting chapters, saving output, validating).

## Layout

```
SKILL.md                       # the agent's instructions (start here)
references/
  ltx2-prompt-guide.md         # distilled LTX-2.3 prompt-writing rulebook (+ verbatim ltx.io golden rules)
  ltx2-official-examples.md    # all 11 verbatim ltx.io example prompts + derived authoring checklist
  ltx2-usage-notes.md          # deep-research findings: model facts, prompt rules, failure fixes, CJK caveat
scripts/
  split_chapters.py            # novel.txt -> one flat chapter-NNN.json per chapter + manifest
  save_scenes.py               # persist a chapter's scenes into its chapter-NNN.json file
  validate.py                  # check prompts + chapter-to-clip mapping integrity
examples/
  the-lantern-road.txt         # tiny English sample novel
  shan-zhong-ye-xing.zh.txt    # Chinese sample (第1章 / 第2章)
  hai-bian-de-xin.zh.txt       # Chinese sample (第一章 / 第二章, kanji numerals)
  yuki-no-eki.ja.txt           # Japanese sample (第一話 / 第二話)
  example-output/              # committed generated projects (EN + ZH + JA), incl. cast sheets
evals/
  evals.json                   # test prompts for the skill (English + Chinese + Japanese)
```

## Plan each chapter as a whole

The agent reads a whole chapter before writing anything and plans it as a unit: it builds
a **cast sheet** (each character with a fixed visual description) and a scene arc, then
writes all of the chapter's scene prompts together, restating each character's canonical
look **verbatim** in every prompt they appear in. Planning holistically — and reusing the
identical anchor phrases rather than paraphrasing them — is what keeps characters,
settings, and continuity consistent from clip to clip (paraphrasing or dropping a
character's description is what makes hair and clothing drift). The cast sheet is persisted
project-wide in `characters.json` so later chapters reuse the same looks.

## Match the novel's language

Prompts are written in the **same language as the source novel** — a Chinese novel gets
Chinese prompts, a Japanese novel Japanese prompts — so voice, tone, and cultural detail
stay consistent. The LTX-2.3 element ordering and mandatory audio layer are the same in
every language; only the words change.

## Quick manual run

```bash
python scripts/split_chapters.py examples/the-lantern-road.txt --out output
# (agent reads each chapter's source_text from chapter-NNN.json and writes the scenes back)
python scripts/save_scenes.py --project output/the-lantern-road --chapter 1 --scenes scenes.json
python scripts/validate.py --project output/the-lantern-road
```

No third-party dependencies for the core scripts — Python 3.8+ standard library only.

## Chaining long sequences (clip continuation)

LTX-2.3 tops out at ~10–20 s per generation, so a continuous stretch of story is rendered
as several short clips. For a seamless seam, mark the continuing scene `continuation: true`
and give the feeding scene an `end_state` (its final-frame framing/pose/lighting); the
continuation prompt then opens from that state and describes only the onward motion.
**DrawThings chains the clips for you**: render the run in order and start each continuation
scene from the previous clip's **last frame** (its native image-to-video / "use last frame"
option), so the character's look carries over pixel-for-pixel. There is no frame-extraction
step in this skill.

`validate.py` flags a `continuation` scene whose predecessor has no `end_state`.

## Spoken dialogue

LTX-2.3 generates speech and lip-sync in the same pass, so a character speaks a line by
having that line written **verbatim in quotes inside the prompt** (in the novel's own
language) — that quoted text is what the model voices. There is **no separate dialogue
input**. Aim to give (nearly) every scene a spoken line; `save_scenes.py` and
`validate.py` report **dialogue coverage** (how many scenes have speech) so you can push it
high. Scenes also carry a structured `dialogue` array (`{"speaker", "line"}`) — this is
**internal metadata in the chapter JSON, not a separate deliverable**; `save_scenes.py` uses it
only to auto-weave any line you forgot to embed and to warn when a line is too long to fit
the clip (estimated at ~2.5 English words or ~5 CJK characters per second). See the
Japanese and Chinese projects under `examples/example-output/` for worked examples with
native-language prompts and dialogue in every scene.

## Negative prompts: author one per scene, in the scene's language

Each scene's `negative_prompt` is **authored by the agent** — the scripts never translate.
Two rules: (1) write it in the **same language as the `prompt`** (Chinese prompt → Chinese
negative, Japanese → Japanese, English → English); (2) **tailor it to the scene** — a small
shared core (on-screen text, subtitles, watermark, warped hands, extra people) plus
scene-specific exclusions (e.g. `bright sunlight` for a night scene, `calm still water` for
a rapids scene). If you omit it, `save_scenes.py` fills a generic **English** fallback for
English prompts only; for a CJK prompt it stays empty and both `save_scenes.py` and
`validate.py` warn you to author a localized one. An English negative on a CJK prompt is
also flagged. See the worked examples under `examples/example-output/` — every scene has a
distinct, native-language negative.

## Audio: weave sound through the action, not in a trailing bracket

LTX-2.3 generates video and audio in one pass, so every prompt needs 3–5 sound cues — but
**thread each sound into the sentence describing the beat it accompanies** rather than
dumping them all in one bracket at the end. A trailing catch-all group (a final
`【风、脚步、鸦啼】` appended after the action) is largely ignored by the model, so ambient
audio parked there never reaches the video. Attach the wind to the moment it blows, the
footsteps to the step, the accent to its beat; a short inline `[sound]` / `【声】` group
beside its own beat mid-paragraph is fine.

## Output: one flat file per chapter

Each chapter produces a single consolidated **`chapter-NNN-<slug>.json`** — it carries the
verbatim `source_text`, the chapter's cast, and every scene's positive prompt, localized
negative prompt, duration, and continuity fields. There are no per-chapter folders and no
separate `source.txt`, `chapter.json`, or `prompts.md`. This one file is both the
deliverable you paste prompts from **and** the machine-readable record that `validate.py`
and regeneration use.

## How output maps back to the novel

Each clip is addressable by **chapter number + scene index**, and every scene stores
the verbatim `source_excerpt` it depicts. To regenerate a clip you didn't like, edit
that chapter's `chapter-NNN.json` (or ask the agent to) and re-run `save_scenes.py` for the
chapter. `validate.py` flags any scene whose excerpt no longer maps to its chapter.
