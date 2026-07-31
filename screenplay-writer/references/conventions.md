# Screenplay conventions — reference

Deeper conventions and edge cases for the screenplay-writer skill. Read this when a scene
needs a structure the base template doesn't cover, or when adapting messy source prose.

## Table of contents
1. Scene heading details
2. Action-line style
3. Dialogue variants (VO / OS / parenthetical)
4. Transitions and special sequences (montage, intercut, flashback)
5. Mode B adaptation heuristics
6. Worked examples

## 1. Scene heading details

`{集数}-{场次} {地点} {时间}{内外景}`

- **集数-场次**: episode and scene index. Scene index restarts each episode (`2-1`, `2-2`…).
- **地点**: the location name, ideally matching a location in the story bible verbatim so the
  storyboard stage can bind it to a scene asset.
- **时间**: 日 / 夜 / 黄昏 / 清晨 / 稍后 (for continuous time), etc.
- **内外景**: 内 (interior) / 外 (exterior). Use 内外 if the scene straddles a threshold.

Keep one location per scene. When characters move to a new place, start a new scene.

## 2. Action-line style

- Every stage direction begins with `▲`.
- Present tense, concrete, visual. Describe what a camera could see, not interior thoughts
  (put those in dialogue or VO).
- One beat per line keeps the text parseable and easy to storyboard.
- Introduce a character's first appearance with a brief visual tag the first time only.

## 3. Dialogue variants

- **On-camera**: `角色名：台词`
- **Voiceover (旁白/内心)**: `角色名（VO）：台词` — narration not tied to lip movement.
- **Off-screen (画外音)**: `角色名（OS）：台词` — the speaker is in the scene but not framed.
- **Parenthetical (语气/动作提示)**: put a short delivery cue in `（）` before the line —
  `林越（冷笑）：原来如此。` Use sparingly; over-directing dialogue is a smell.

## 4. Transitions and special sequences

- **Transition cue**: on its own line in `【】` — `【叠化】`, `【黑场】`, `【硬切】`.
- **Montage (蒙太奇)**: head the block with `【蒙太奇开始】` / `【蒙太奇结束】` and list beats
  as short `▲` lines; each beat may carry its own mini scene heading if locations differ.
- **Intercut (交叉剪辑)**: mark `【交叉剪辑：A线 / B线】` and label action lines with `A:` / `B:`.
- **Flashback (闪回)**: wrap with `【闪回开始】` / `【闪回结束】`; put the era in the scene
  heading time slot if it helps (`3-4 老宅 1998·夜 内`).

## 5. Mode B adaptation heuristics

When converting finished prose:

- **Coverage discipline**: process only chapters/sections actually provided. Note explicitly
  in your summary how many you covered if the source implies more.
- **Dialogue extraction**: lift spoken lines from the prose; convert reported speech
  ("他说他会回来") into either action + implied beat or leave as narration — don't fabricate
  verbatim quotes that aren't in the text.
- **Interiority → VO or action**: a character's unspoken thoughts become `（VO）` only if the
  work uses narration; otherwise externalize them as visible action.
- **Scene segmentation**: cut a new scene at each change of location or significant time jump,
  even if the prose runs them together in one paragraph.

## 6. Worked examples

### Mode A — from a one-line premise

Input: "一个退役刑警被拉回一桩十年前的悬案。写1集。"

```markdown
## 第 1 集：旧案重启
> 概述：退役刑警周detach…（200–400字，紧扣前提展开该集走向）

### 1-1 周家旧宅 夜 内
▲ 周立山盯着墙上泛黄的案卷照片，烟灰簌簌落下。
【推近至特写：照片上被红笔圈住的女孩】
周立山（VO）：十年了，我以为这辈子不用再看见你。
▲ 手机骤响，屏幕跳出一个陌生号码。
周立山：……喂？
陌生男声（OS）：周队，第二个女孩，找到了。
```

### Mode B — from prose

Source prose: "林越冲进雨里，追着那辆黑车跑了两条街，最终瘫倒在积水中，看着尾灯消失。"

```markdown
### 4-2 老城区街道 夜 外
▲ 林越冲进雨幕，朝一辆黑色轿车狂追。
▲ 连过两个街口，雨水灌进领口，脚步渐乱。
▲ 他脱力瘫倒在积水中，抬头。
【尾灯在雨中散成一片模糊的红，消失】
```

Note how one prose sentence becomes several `▲` beats and a `【】` cue — segmented so each
line maps cleanly to a future shot.
