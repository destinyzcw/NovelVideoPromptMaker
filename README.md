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
  split_chapters.py            # novel.txt -> per-chapter folders + manifest
  save_scenes.py               # persist a chapter's scenes as paste-ready prompt files
  validate.py                  # check prompts + chapter-to-clip mapping integrity
examples/
  the-lantern-road.txt         # tiny English sample novel
  shan-zhong-ye-xing.zh.txt    # Chinese sample (第1章 / 第2章)
  hai-bian-de-xin.zh.txt       # Chinese sample (第一章 / 第二章, kanji numerals)
  yuki-no-eki.ja.txt           # Japanese sample (第一話 / 第二話)
  example-output/              # committed generated projects (EN + ZH + JA), incl. transcripts + cast sheets
evals/
  evals.json                   # test prompts for the skill (English + Chinese + Japanese)
```

## Plan each chapter as a whole

The agent reads a whole chapter before writing anything and plans it as a unit: it builds
a **cast sheet** (each character with a fixed visual description) and a scene arc, then
writes all of the chapter's scene prompts together, reusing the same character
descriptions. Planning holistically — rather than chunking the text and prompting each
fragment in isolation — is what keeps characters, settings, and continuity consistent
from clip to clip. The cast sheet is persisted project-wide in `characters.json` so later
chapters reuse the same looks.

## Match the novel's language

Prompts are written in the **same language as the source novel** — a Chinese novel gets
Chinese prompts, a Japanese novel Japanese prompts — so voice, tone, and cultural detail
stay consistent. The LTX-2.3 element ordering and mandatory audio layer are the same in
every language; only the words change.

## Quick manual run

```bash
python scripts/split_chapters.py examples/the-lantern-road.txt --out output
# (agent reads each chapter's source.txt and writes scenes.json)
python scripts/save_scenes.py --project output/the-lantern-road --chapter 1 --scenes scenes.json
python scripts/validate.py --project output/the-lantern-road
```

No third-party dependencies — Python 3.8+ standard library only.

## Spoken dialogue & transcripts

LTX-2.3 generates speech and lip-sync in the same pass, so a character speaks a line by
having that line written **verbatim in quotes inside the prompt** (in the novel's own
language) — that quoted text is the transcript the model voices. Aim to give (nearly)
every scene a spoken line; `save_scenes.py` and `validate.py` report **dialogue coverage**
(how many scenes have speech) so you can push it high. Scenes also carry a structured
`dialogue` array (`{"speaker", "line"}`); `save_scenes.py` uses it to emit a per-chapter
`transcript.txt`, to auto-weave any line you forgot to embed, and to warn when a line is
too long to fit the clip (estimated at ~2.5 English words or ~5 CJK characters per
second). See the Japanese and Chinese projects under `examples/example-output/` for
worked examples with native-language prompts and dialogue in every scene.

## How output maps back to the novel

Each clip is addressable by **chapter number + scene index**, and every scene stores
the verbatim `source_excerpt` it depicts. To regenerate a clip you didn't like, edit
that chapter's `scenes.json` (or ask the agent to) and re-run `save_scenes.py` for the
chapter. `validate.py` flags any scene whose excerpt no longer maps to its chapter.
