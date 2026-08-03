# LTX-2.3 video prompt playbook (FLF2V, first-frame → last-frame)

The storyboard skill's **video prompts** target **LTX-2.3** (Lightricks) — an
open-source **audio+video** model natively supported in ComfyUI. We use its
**FLF2V** (First-Last-Frame → Video) workflow: give it two adjacent keyframes
(from Z-Image Turbo) as the start/end images, plus one text prompt that describes
the motion, narrative, and audio for that transition. LTX-2.3 interpolates a
coherent clip between the two frames **and generates synchronized audio, including
dialogue**. A shot is authored as a **keyframe chain** (see "Chaining" below), so
each shot yields **one prompt per adjacent pair** — several short clips that
concatenate. (Actual video generation is out of scope for this repo — we only
author the prompts so they're ready for LTX-2.3.)

Sources: Lightricks LTX-2.3; ComfyUI LTX-2.3 tutorial (T2V/I2V/**FLF2V**/IA2V);
LTX-2 prompting guide; ComfyUI chaining guide.

## What LTX-2.3 is (facts that shape the prompt)

- **Audio+video in one pass.** It renders **dialogue, narration (VO), ambient
  sound, SFX, and music** timed to the picture. So the screenplay's 台词 and
  VO/旁白 belong **in the prompt**, not dropped — this is how narrative survives
  into the video stage.
- **FLF2V is image-conditioned.** The two anchor frames (from Z-Image Turbo)
  carry identity, composition, style, and lighting. The prompt should therefore
  focus on **motion + timing + audio + narrative**, not re-describe the anchors'
  fixed appearance (the frames already fix that).
- **Text encoder = Gemma-3-12B.** It reads natural-language, instruction-style
  prose and is multilingual. Keep the paragraph coherent and present-tense.
- Native 4K / up to 50 fps / up to ~20 s clips. Storyboard shots are short
  (2–10 s) — state the intended duration/pacing.

## Chaining — keyframe chain & one clip per small delta

**Why chain at all.** FLF2V interpolates cleanly only when the first and last
frames differ by a *small* motion; the official guidance is to "keep the subject,
composition, and orientation similar between anchors." A large jump (a fall, a
body flung across frame, a big camera move, a full pose swap) between one 首帧 and
one 尾帧 makes LTX morph, warp, or slide unrealistically. So a shot is **not** one
big first→last pair — it's a **keyframe chain** `K0 → K1 → … → Kn` where every
adjacent pair is a small, interpolatable beat.

**One clip per segment.** Each pair `Ki → Ki+1` is one FLF2V clip with its own
prompt; play the clips in order to get the shot. Target **~2–4 s per clip** (LTX
supports up to ~20 s, and 4–8 s stays consistent, but small-delta interpolation is
crispest at a few seconds). Add a keyframe wherever a single beat would otherwise
be too big — that's the storyboard skill's *delta budget*.

**Seamless joins.** Chain by making the **last frame of clip *i* the first frame
of clip *i+1*** — the *same rendered image*, not a re-render. The whole chain also
shares **one Z-Image seed**, so identity/lighting stay put across the join.

**Fight drift.** Over a long chain, character/scene detail can wander. From the
**2nd clip onward, restate a short identity cue** for the key subject ("白衣的赵
天骄") inside the motion prompt — a light reminder, not the full anchor phrase
(anchors still never go into the video prompt).

**Where audio goes.** Attach each 台词/VO/SFX to the **clip where it actually
happens**, not spread across the shot — e.g. a taunt during the wind-up clip, the
VO on the fall clip.

Sources: ComfyUI LTX-2.3 tutorial (large-motion caveat); ComfyUI chaining guide
(last-frame→first-frame, reinforce later prompts); LTX-2.3 clip-length notes.

## Prompt shape — a single present-tense mini-screenplay

Write **one flowing paragraph** (no bullet lists), in **present tense**, that
choreographs the shot from 首帧 to 尾帧. Fold in these six elements in narrative
order, using temporal connectors (`as / then / while / before / after / 随后 /
接着 / 与此同时`):

1. **Shot & camera** — reuse the shot's 景别/机位, then the **camera movement**
   (固定/推/拉/摇/移/跟/手持/俯拍下摇…) and its speed; relate the move to the
   action ("镜头随他抬腿而侧移").
2. **Scene setting** — only the *moving* atmosphere (wind, fog drift, light
   flicker); don't re-list the anchor's fixed decor.
3. **Action** — the subject's motion across the beat, matching the gap between
   首帧 and 尾帧, with cause→effect and small physical detail ("脚发力，少年后弓、
   双脚离地").
4. **Character** — express emotion through **body language**, not labels
   ("眉头紧锁、嘴角抽动"), consistent with the frames.
5. **Camera behavior** — explicit perspective/speed changes over the clip.
6. **Audio (this is where narrative + dialogue live)** —
   - **Dialogue** in quotation marks with **speaker + tone**:
     `赵天骄冷笑着说：“一个废物，也配觊觎宗门功法？”` /
     `Emma (whispering): "..."`. Keep the screenplay's lines verbatim.
   - **Narration / VO / 旁白 / 内心独白** as a spoken line, tagged:
     `林越（画外音，压抑）：“我不甘心……”`.
   - **Ambient + SFX**: 风声骤起、碎石滚落、衣袂猎猎、掌风闷响.
   - Optional **music** bed if the scene wants it.
   Order audio events in the sequence they should occur, aligned to the action.

End with a short **guardrail** clause: `画面无字幕、无水印、无台词字幕文字`
(so speech is voiced, not printed on screen), plus `无闪烁、动作连贯`.

## Language note

Write the motion/scene description in the project's language (中文 here) so it
matches the screenplay and keeps dialogue/VO **verbatim**. Gemma-3 is
multilingual; if you find motion fidelity improves in English for a given setup,
you may describe the *action/camera* in English but **keep the dialogue and VO
lines in their original language** so speech stays faithful. Never translate a
character's line just to fit the model.

## Duration & pacing

State the clip length and how energy changes: `约4秒，前段蓄力停顿、后段爆发失重`.
Give one clause of pacing — LTX responds to explicit timing.

## Worked example (a 2-clip chain, keeps narrative + dialogue)

Shot 2-3-05 (赵天骄 踹落 林越) is a big motion (蓄力 → 踹中 → 越崖坠出), so it's a
**3-keyframe chain → 2 clips**: K0 抬腿蓄力, K1 踹实、少年后弓双脚离地（还未离崖）,
K2 少年越过崖线坠入冷雾。One prompt per adjacent pair:

**片段 1 — K0 → K1 (踹击瞬间):**

```text
中近景侧面平视，镜头随白衣青年抬腿而快速侧向横移、并轻微跟随；狂风在断崖边骤然增强，
墨色雾气与碎叶横掠画面。白衣青年冷笑发力，一脚踹出；随后少年身体猛地后弓、双脚离地，
但仍未越出崖线，死死抱住怀中玉简，碎石在两人脚边震起。赵天骄冷笑着、语气轻蔑地说：
“一个废物，也配觊觎宗门功法？”掌风闷响、靴底踏石声、衣袂猎猎与崖下风啸铺满声场，
低沉弦乐在踹实瞬间下压。约3秒，前段短暂蓄力、后段猛烈命中。画面无字幕、无水印、
无台词文字，动作连贯、无闪烁。
```

**片段 2 — K1 → K2 (坠出崖线):**

```text
远景高角度俯视，镜头从崖边向外跟摇并轻微下坠；狂风把冷雾向上卷起。白衣的赵天骄立在
崖边收势，少年抱紧玉简越过崖线、整个人向崖外坠去，身体在空中失衡旋转、迅速变小，碎石
从他身旁滚落进深雾。随着少年坠出崖线，林越（画外音，压抑而不甘）：“我不甘心……”。
崖风呼啸、碎石坠落声与低沉弦乐一起拉长，声音空间从近处骤然扩成空旷深谷。约4秒，
前段越线失重、后段坠向冷雾。画面无字幕、无水印、无台词文字，动作连贯、无闪烁。
```

Notes: each paragraph is present-tense and continuous, describing only the *motion*
of one small beat (the frames fix appearance). The kick's taunt sits on 片段 1, the
VO on the fall in 片段 2 — audio attached to the clip where it happens. 片段 2 restates
"白衣的赵天骄" as a light drift reminder. K1 is rendered once and is the end of 片段 1
and the start of 片段 2, so the join is seamless. Both keep the screenplay lines
verbatim with speaker + tone and end with guardrails so speech is voiced, not
subtitled.
