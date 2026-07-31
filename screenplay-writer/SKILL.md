---
name: screenplay-writer
description: >-
  Turn a story synopsis, outline, or existing prose into a structured, multi-episode
  screenplay (剧本) with episodes → scenes → dialogue, using industry scene-heading,
  action, voiceover, and camera-cue conventions. Use this whenever the user wants to
  write, draft, expand, or adapt a 剧本 / screenplay / 分集剧本 / 剧本大纲, convert a novel
  chapter or story synopsis into scenes and dialogue, break a story into episodes and
  scenes, or produce shootable script text — even if they just say "把这个故事写成剧本",
  "写个剧本", "adapt this into a script", or "拆成分集". This is the first stage before
  storyboard/分镜 work; pair it with the storyboard-prompt skill for shot design.
---

# Screenplay Writer (剧本)

Adapt a story into a structured screenplay the way a professional writers' room does:
first lock the story bible (characters, locations, props), then plan episode outlines,
then write each episode's scenes and dialogue. The hard part is not prose — it's
**consistency across a long work and discipline against drift**. This skill exists to
enforce that discipline while leaving the creative writing to your own judgment.

## Two modes — detect which one applies

**Mode A — Generate from outline** (input is a synopsis, premise, or per-episode outline):
you invent the scenes and dialogue, but only as a faithful expansion of the outline.

**Mode B — Adapt existing text** (input is finished prose, a novel, or a full draft
script): you restructure what is already written. You may only use content that exists
in the source. If the user gives you 2 chapters, you produce scenes for those 2 chapters
and stop — never fabricate later events, even if the plot is obvious.

If unsure which mode, ask one question. Most "写成剧本" requests on existing prose are Mode B.

## Workflow

Work in three passes. Treat each pass as a real step you complete before the next — the
whole point is that later passes stay anchored to earlier decisions.

### Pass 1 — Story bible

Extract (Mode B) or design (Mode A) the recurring entities and record them once so every
scene references them identically:

- **Characters (角色)** — one canonical name each (see naming rules below), plus a one-line
  description and role (主角 / 配角 / 龙套).
- **Locations (场景)** — the physical places scenes happen in.
- **Props (道具)** — objects that matter to the plot.

Also capture **genre/tone (类型)** and a **story synopsis (故事梗概)**. In Mode B, the
synopsis summarizes only what the provided text covers.

### Pass 2 — Episode plan

Decide the episode breakdown. If the user asked for N episodes, produce exactly N — do not
silently add or drop episodes. For each episode write a **200–400 character synopsis
(概述)** describing that episode's plot trajectory. This synopsis is the contract the
next pass must honor. In Mode B, detect natural episode/chapter boundaries from the source
instead of inventing them; if there are none, treat it as a single episode.

### Pass 3 — Scenes and dialogue (the loop)

Process **every** episode from the plan — one at a time, in order, none skipped. For each
episode, write **3–8 scenes**. For each scene decide location, time, interior/exterior,
which characters/props appear, then write the action and dialogue.

This is a loop, not a sample. Never stop early with "剩余集数同理" / "以此类推" / "for
brevity". Before you report done, verify the number of episodes you wrote equals the plan.

## Formatting conventions

Follow these exactly — they are what makes the output read as a real 剧本 and what the
downstream storyboard stage parses.

- **Scene heading**: `{集数}-{场次} {地点} {时间}{内外景}` — e.g. `1-3 咖啡馆 日 内`
  (time is 日/夜/黄昏…, 内 = interior, 外 = exterior).
- **Action / stage direction**: prefix each line with `▲` — e.g. `▲ 林越推门而入，雨水顺着风衣滴落。`
- **Voiceover / narration**: mark with `VO` — e.g. `林越（VO）：那一年，我还不懂什么叫代价。`
- **Camera / shot instruction** (optional, use sparingly): wrap in `【】` — e.g. `【推近至特写】`
- **Dialogue**: `角色名：台词内容` — e.g. `林越：你早就知道了，对吗？`

## Output template

Produce Markdown. Use this structure:

```markdown
# 剧本：{标题}
**类型**：{genre}　**集数**：{N}

## 人物表
- **{角色名}**（主角/配角/龙套）：{一句话描述，别名可在此注明}
- ...

## 场景 / 道具
- 场景：{地点1}、{地点2} …
- 道具：{道具1}、{道具2} …

## 故事梗概
{synopsis}

---

## 第 1 集：{集标题}
> 概述：{200–400字}

### 1-1 {地点} {时间}{内外景}
▲ {动作描写}
{角色名}：{台词}
{角色名}（VO）：{旁白}
【{镜头指令}】
...

### 1-2 ...
```

## Discipline rules (why they matter)

- **Naming consistency** — a character has exactly one name throughout. Don't join names
  with "/" (`王德发/花非烟` is wrong). For transformations/rebirth/aliases, pick the name
  that appears most, and note the other identity in the character description
  (`王德发，穿越后化名花非烟`). Downstream shots and asset references break if a character
  is referred to two ways.
- **Stay within the outline** — in Mode A, expand and enrich the episode synopsis; don't
  invent plot the outline doesn't imply. In Mode B, never write beyond the supplied text.
  Drift is the most common failure and it silently corrupts continuity.
- **Dialogue carries character** — voice should match each character's personality from the
  bible, and pace should follow the episode synopsis's rhythm.
- **Finish the work** — every planned episode gets scenes. Partial delivery with a promise
  to "continue later" defeats the purpose.

For deeper conventions, edge cases (montage, intercut, flashback markers) and worked
examples, read `references/conventions.md`.
