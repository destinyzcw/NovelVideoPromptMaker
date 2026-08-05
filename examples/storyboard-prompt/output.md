# MiniMax-H3 分镜示例：断魂崖

## 分镜：第 2 集 · 2-3 断魂崖

**画风**：国风水墨与写实结合，冷色调电影感，高反差夜景，冷调月光穿过体积雾，细腻胶片颗粒。

**视觉锚点**

- 林越：约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤
- 赵天骄：二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍
- 断魂崖：陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾
- 残破玉简：巴掌大的残破玉简，边缘焦黑，表面暗金云纹

**说话人**

- 赵天骄 → S1：年轻男性中低音，冷静、傲慢、语速偏慢
- 林越 → S2：年轻男性中音，受伤后气息不稳但意志坚定

| 镜号 | 时长 | 景别/机位 | 运镜 | 起点→过程→落点 | 台词/VO | 声音 | H3模式 |
|---|---:|---|---|---|---|---|---|
| 01 | 6s | 全景/侧面平视 | 快速小幅跟移 | 掌风命中→后飞→撞上枯树 | 无 | 掌风、撞木、崖风 | FL2VA |
| 02 | 6s | 中景/低角度 | 慢速小幅推近 | 迈步逼近→停住俯视→说完冷笑 | 赵天骄：一个废物，也配觊觎宗门功法？ | 脚步、碎石、低弦 | FL2VA |
| 03 | 6s | 近景/平视 | 慢速小幅推近 | 伏地喘息→撑起上身→攥紧玉简 | 林越：这功法……是我的。 | 呼吸、衣料、玉简轻鸣 | FL2VA |
| 04 | 8s | 全景/侧面平视 | 快速跟移后向外下摇 | 抬腿蓄力→踹中→越崖坠落 | 林越（VO）：我不甘心…… | 踹击、碎石、风啸、弦乐骤停 | FL2VA |

## 镜号 01

**模式与请求参数**：MiniMax-H3 FL2VA｜duration=6｜resolution=2K｜ratio=adaptive

**Picture 1 / K0 首帧 — Z-Image Turbo**

```text
电影感全景侧面平视，画面左侧是约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，胸口刚被隔空掌风命中，身体开始向后离地，双臂本能护住巴掌大的残破玉简，边缘焦黑，表面暗金云纹；画面右侧是二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，单掌向前推出。环境为陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾，碎石和衣袂被掌风掀起。冷调月光从侧后方勾出轮廓，体积雾穿过枯枝。国风水墨与写实结合，冷色调电影感，高反差夜景，细腻胶片颗粒。画面干净，无文字、无水印、无多余人物，正确的手部与肢体结构。
```

参数：steps 9｜cfg 0｜1280×720｜固定 seed=2301

**Picture 2 / K1 尾帧 — Z-Image Turbo**

```text
电影感全景侧面平视，画面左侧是约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，背部重重撞在崖边枯树上，身体弓起，嘴角溅血，双臂仍护住巴掌大的残破玉简，边缘焦黑，表面暗金云纹；画面右侧是二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，已经收掌并冷眼旁观。环境为陡峭黑岩断崖，崖边枯树剧烈弯折，崖下深不见底的冷雾，断枝和碎石悬在撞击后的空气中。冷调月光从侧后方勾出轮廓，体积雾穿过枯枝。国风水墨与写实结合，冷色调电影感，高反差夜景，细腻胶片颗粒。画面干净，无文字、无水印、无多余人物，正确的手部与肢体结构。
```

参数：steps 9｜cfg 0｜1280×720｜固定 seed=2301

**MiniMax-H3 FL2VA prompt**

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 6.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Cinematic Chinese wuxia fantasy with realistic ink-wash texture, a wide side-view shot begins in the character positions, cold moonlight, black-rock cliff environment, and composition established by Picture 1. The camera tracks left with small amplitude at fast speed as the force of the palm strike drives the injured young disciple backward through the crosswind. His torso bends from the impact, both feet leave the ground, and he clamps both arms around the damaged jade slip while his robe and tied hair stream behind him. Loose gravel and dead leaves scatter along his path. He crosses the short distance to the dead tree, strikes the trunk hard with his back, and settles into the bent body position, character spacing, broken branches, and final composition established by Picture 2. The white-robed attacker remains planted in the background and lowers his striking hand as the disciple hits the tree.

overall_soundscape: Strong cliff wind continues throughout the shot. A compressed palm-force boom is followed by rushing cloth, gravel scattering across rock, and a heavy wooden impact with branches cracking.

non_diegetic_music: Low taiko pulses and sustained bass strings at a slow tempo rise under the backward flight, ending on one heavy accent at the tree impact.
```

**API素材映射**：Picture 1 → `first_frame`; Picture 2 → `last_frame`.

## 镜号 02

**模式与请求参数**：MiniMax-H3 FL2VA｜duration=6｜resolution=2K｜ratio=adaptive

**Picture 1 / K0 首帧 — Z-Image Turbo**

```text
电影感中景低角度仰视，画面下方前景是约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，倒在枯树旁急促喘息，怀中露出巴掌大的残破玉简，边缘焦黑，表面暗金云纹；画面上方远处是二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，刚从风雾里迈出第一步。陡峭黑岩断崖、枯树和深不见底的冷雾保持清晰空间关系。冷调月光形成侧逆光，体积雾切开深蓝夜色。国风水墨与写实结合，冷色调电影感，高反差夜景，细腻胶片颗粒。画面干净，无文字、无水印、无多余人物。
```

参数：steps 9｜cfg 0｜1280×720｜固定 seed=2302

**Picture 2 / K1 尾帧 — Z-Image Turbo**

```text
电影感中景低角度仰视，画面下方前景是约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，仍倒在枯树旁并护住怀中残破玉简；画面上方近处是二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，已经停在少年身前，垂眼俯视，嘴角保持轻蔑冷笑。陡峭黑岩断崖、枯树和深不见底的冷雾保持与首帧一致。冷调月光形成侧逆光，体积雾切开深蓝夜色。国风水墨与写实结合，冷色调电影感，高反差夜景，细腻胶片颗粒。画面干净，无文字、无水印、无多余人物。
```

参数：steps 9｜cfg 0｜1280×720｜固定 seed=2302

**MiniMax-H3 FL2VA prompt**

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 6.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Cinematic Chinese wuxia fantasy, a medium low-angle shot begins in the composition and cold moonlit cliff environment established by Picture 1. The camera pushes in with small amplitude at slow speed as the tall white-robed young man with a cold, controlled baritone (S1) walks toward the injured disciple. Each measured step grinds loose stones beneath his boots while his silver-trimmed robe snaps in the crosswind. He slows, stops beside the dead tree, lowers his gaze, and settles into the final spacing, posture, and contemptuous expression established by Picture 2. After a brief silent pause, the white-robed young man (S1) says in a quiet, disdainful tone: <d>[Chinese] 一个废物，也配觊觎宗门功法？</d> His lips close after the final syllable and the cold smile remains.

overall_soundscape: Strong wind moves continuously over the cliff. Even footsteps approach across black rock, loose gravel rolls beneath each boot, and robe fabric snaps sharply before the movement stops for the spoken line.

non_diegetic_music: Sustained low strings at a slow tempo increase gradually during the approach, then hold one quiet unresolved note beneath the dialogue.
```

**API素材映射**：Picture 1 → `first_frame`; Picture 2 → `last_frame`.

## 镜号 03

**模式与请求参数**：MiniMax-H3 FL2VA｜duration=6｜resolution=2K｜ratio=adaptive

**Picture 1 / K0 首帧 — Z-Image Turbo**

```text
电影感近景平视，约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，伏在黑岩地面急促喘息，嘴角带血，一只手刚触到怀中巴掌大的残破玉简，边缘焦黑，表面暗金云纹；背景虚化为枯树、黑岩断崖和深冷雾，狂风把乱发和衣襟吹向同一方向。冷调月光照亮半张脸，体积雾从肩后流过。国风水墨与写实结合，冷色调电影感，高反差夜景，细腻胶片颗粒。画面中只有林越，无文字、无水印，正确的手部结构。
```

参数：steps 9｜cfg 0｜1280×720｜固定 seed=2303

**Picture 2 / K1 尾帧 — Z-Image Turbo**

```text
电影感近景平视，约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，已经用手臂撑起上身，嘴角带血，另一只手死死攥紧怀中巴掌大的残破玉简，边缘焦黑，表面暗金云纹，抬眼坚定地看向画外；背景虚化为枯树、黑岩断崖和深冷雾，狂风把乱发和衣襟吹向同一方向。冷调月光照亮半张脸，体积雾从肩后流过。国风水墨与写实结合，冷色调电影感，高反差夜景，细腻胶片颗粒。画面中只有林越，无文字、无水印，正确的手部结构。
```

参数：steps 9｜cfg 0｜1280×720｜固定 seed=2303

**MiniMax-H3 FL2VA prompt**

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 6.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Cinematic Chinese wuxia fantasy, a close eye-level shot begins in the framing, injured appearance, cold moonlight, and ground position established by Picture 1. The camera pushes in with small amplitude at slow speed as the young disciple with a strained but determined voice (S2) drags a shallow breath into his chest. His fingers find the damaged jade slip, curl around its scorched edge, and tighten until his knuckles pale. He plants his other palm against the rock, lifts his shoulders, and gradually pushes his upper body upright while blood moves slowly from the corner of his mouth. He raises his gaze toward the unseen attacker and settles into the supported posture, clenched hand, and final composition established by Picture 2. The young disciple (S2) says through uneven breathing but with firm emphasis: <d>[Chinese] 这功法……是我的。</d> His lips close as he continues staring upward.

overall_soundscape: Cliff wind remains present but slightly muffled in the close framing. Strained breathing, cloth scraping over stone, a palm pressing into gravel, and a faint resonant vibration from the jade slip are clearly audible.

non_diegetic_music: A single sustained cello note at a slow tempo enters as his hand closes around the jade slip and grows slightly louder beneath the dialogue.
```

**API素材映射**：Picture 1 → `first_frame`; Picture 2 → `last_frame`.

## 镜号 04

**模式与请求参数**：MiniMax-H3 FL2VA｜duration=8｜resolution=2K｜ratio=adaptive

**Picture 1 / K0 首帧 — Z-Image Turbo**

```text
电影感全景侧面平视，画面左侧是约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，抱紧残破玉简站在悬崖边线前，身体因伤势绷紧；画面右侧是二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，右脚后撤、抬腿蓄力，脚尖尚未触及少年。环境为陡峭黑岩断崖，崖边一株枯树，崖下深不见底的冷雾，碎石在两人脚边松动。冷调月光侧逆光勾出轮廓，体积雾向上翻卷。国风水墨与写实结合，冷色调电影感，高反差夜景，细腻胶片颗粒。画面干净，无文字、无水印、无多余人物，正确的肢体结构。
```

参数：steps 9｜cfg 0｜1280×720｜固定 seed=2304

**Picture 2 / K1 尾帧 — Z-Image Turbo**

```text
电影感全景侧面平视并略向崖外俯看，画面右侧是二十岁左右白衣青年，身形修长，玉冠束发，眉眼锋利，银纹宗门长袍，已经收腿立在崖边冷眼旁观；画面左下方是约十六岁少年，清瘦，短束发，粗布外门弟子服，左眉有细疤，双臂抱紧残破玉简，已经越过悬崖边线并向冷雾中坠落，身体开始失衡。环境为陡峭黑岩断崖、崖边枯树和深不见底的冷雾，碎石随少年一起坠下。冷调月光侧逆光勾出轮廓，体积雾从崖下翻卷。国风水墨与写实结合，冷色调电影感，高反差夜景，细腻胶片颗粒。画面干净，无文字、无水印、无多余人物，正确的肢体结构。
```

参数：steps 9｜cfg 0｜1280×720｜固定 seed=2304

**MiniMax-H3 FL2VA prompt**

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 8.00-second mark of the target video.

integrated_multimodal_description: [Shot 1] Cinematic Chinese wuxia fantasy, a wide side-view shot begins in the character poses, cliff-edge spacing, cold moonlight, and composition established by Picture 1. The camera tracks left with small amplitude at fast speed as the white-robed attacker shifts his weight forward, drives his raised leg outward, and strikes the injured disciple in the torso. The disciple's body bends around the impact, both feet leave the rock, and his arms lock around the damaged jade slip. Loose gravel bursts from the cliff edge as the attacker retracts his leg. The camera continues tracking the disciple, then tilts down with small amplitude as he crosses the cliff line, loses balance in open air, and begins falling into the rising fog. The attacker remains at the edge while the disciple settles into the falling position, scale, spacing, and final composition established by Picture 2. As the disciple falls, the young disciple (S2) says in an off-screen voiceover with suppressed rage: <d>[Chinese] 我不甘心……</d> while his on-screen lips remain completely closed.

overall_soundscape: Violent cliff wind fills the stereo field. A sharp boot impact is followed by a body thud, cloth snapping, gravel breaking loose, and stones falling into the deep ravine as the wind opens into a larger hollow space.

non_diegetic_music: Low strings and a slow taiko pulse build during the kick, swell as the disciple crosses the cliff edge, and stop abruptly after the voiceover, leaving only wind for the final second.
```

**API素材映射**：Picture 1 → `first_frame`; Picture 2 → `last_frame`.
