# LTX-2.3 video prompt playbook (FLF2V, first-frame → last-frame)

The storyboard skill's **video prompt** targets **LTX-2.3** (Lightricks) — an
open-source **audio+video** model natively supported in ComfyUI. We use its
**FLF2V** (First-Last-Frame → Video) workflow: give it the shot's 首帧 as the
start image and 尾帧 as the end image, plus one text prompt that describes the
motion, narrative, and audio for the transition. LTX-2.3 interpolates a coherent
clip between the two frames **and generates synchronized audio, including
dialogue**. (Actual video generation is out of scope for this repo — we only
author the prompt so it's ready for LTX-2.3.)

Sources: Lightricks LTX-2.3; ComfyUI LTX-2.3 tutorial (T2V/I2V/**FLF2V**/IA2V);
LTX-2 prompting guide.

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

## Worked example (keeps narrative + dialogue)

Shot 2-3-06 (赵天骄 踹落 林越), 首帧 = 抬腿蓄力, 尾帧 = 踹中、少年越过崖线：

```text
全景侧面平视，镜头随白衣青年抬腿而缓慢侧向横移、并轻微跟随；狂风在断崖边骤然增强，
墨色雾气与碎叶横掠画面。白衣青年冷笑发力，一脚踹出；随后少年身体猛地后弓、双脚离地、
越过崖边线向崖外坠出，碎石被踢飞、向崖下卷落，两人衣袂与少年乱发在风中剧烈翻飞。
赵天骄冷笑着、语气轻蔑地说：“一个废物，也配觊觎宗门功法？”接着，随着少年坠出崖线，
林越（画外音，压抑而不甘）：“我不甘心……”。掌风闷响、狂风呼啸、碎石滚落声铺满声场，
低沉的弦乐随坠落感压下。约4秒，前段短暂蓄力停顿、后段急促失重。画面无字幕、无水印、
无台词文字，动作连贯、无闪烁。
```

Notes: the paragraph is present-tense and continuous; it describes only the
*motion* (the frames already fix appearance); it keeps the exact screenplay line
and the VO, each tagged with speaker + tone; ambient SFX and a music cue are
ordered with the action; it ends with guardrails so the dialogue is spoken, not
subtitled.
