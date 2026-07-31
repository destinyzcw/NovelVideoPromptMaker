# Test input — storyboard-prompt

User prompt given to an agent that had the `storyboard-prompt` skill available:

> 给下面这场戏做分镜，并生成每个镜头的分镜图提示词。画风：国风水墨与写实结合、冷色调、电影感。这场戏：
>
> ### 2-3 断魂崖 夜 外
> ▲ 狂风大作，林越被赵天骄一掌击飞，撞在崖边枯树上。
> ▲ 赵天骄缓步逼近，眼神轻蔑。
> 赵天骄：一个废物，也配觊觎宗门功法？
> ▲ 林越挣扎起身，嘴角带血，死死攥着怀中玉简。
> 林越：这功法……是我的。
> ▲ 赵天骄冷笑，一脚将他踹下悬崖。
> 林越（VO）：我不甘心……
>
> Assets available: 林越(初始)、赵天骄(初始)、断魂崖(场景)、残破玉简(道具)。

Note: this scene is the same 断魂崖 beat referenced in the screenplay example, so the two
skills can be seen working as a two-stage pipeline (剧本 → 分镜图 prompt).

See `output.md` for the produced shot list and per-shot image prompts.
