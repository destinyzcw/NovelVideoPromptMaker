# NovelVideoPromptMaker

Prompt-authoring skills for a story-to-video workflow:

1. turn a story, outline, or novel excerpt into a structured screenplay;
2. turn screenplay scenes into machine-readable image and MiniMax-H3 video prompts.

The project generates prompts only. It does not call image or video backends, render media,
manage ComfyUI, or run visual-QA loops.

The default visual direction is **original Japanese theatrical 2D animation**: expressive
hand-drawn linework, controlled cel shading, painted backgrounds, deliberate color scripts, and
animation-aware motion. Prompts avoid live-action and photoreal rendering unless a user explicitly
requests another style.

## Skills

| Skill | Input | Output |
|---|---|---|
| [`screenplay-writer`](screenplay-writer/SKILL.md) | Story synopsis, outline, or prose | Markdown screenplay with episodes, scenes, action, dialogue, VO, and sound cues |
| [`storyboard-prompt`](storyboard-prompt/SKILL.md) | Screenplay scene plus optional references | Strict JSON array: one object per approximately 5-10 second video piece, including image inputs, image prompts, H3 settings, and the complete video prompt |

The two stages chain directly:

```text
story / prose -> screenplay-writer -> screenplay -> storyboard-prompt -> JSON prompt objects
```

## MiniMax-H3 design

- **Split prompt languages:** Z-Image prompts use the source language and stay monolingual;
  MiniMax-H3 prompt prose uses English. Verbatim dialogue, lyrics, and visible text retain their
  source language.
- **Animation-first style contract:** every image and video prompt repeats stable Japanese 2D
  animation anchors, keeps character designs visibly illustrated, and directs key poses,
  anticipation, follow-through, held reactions, and selective effects animation.
- **Ref2VA-first narrative workflow:** character-driven pieces normally use critical reference
  images for identity, costume, setting, style, props, expressions, or decisive compositions.
  These images may depict any important moment and use API role `reference_image`. Each piece
  uses at most two reference images; more complex action is split into additional pieces.
- **Endpoint modes remain available:** FL2VA, I2VA, and L2VA are used only when exact opening
  or ending frames matter.
- **Short production units:** each JSON object represents one independent H3 request, normally
  lasting 5-10 seconds.
- **Self-contained objects:** each item includes its shot intent, dialogue events, required
  image inputs, image-generation prompts and parameters, H3 request settings, and video prompt.

## JSON output

`storyboard-prompt` returns raw, parseable JSON with no Markdown wrapper or explanatory prose:

```json
[
  {
    "piece_id": "2-3-01",
    "source_scene": "2-3 Soul-Breaking Cliff",
    "duration_seconds": 7,
    "h3_mode": "ref2va",
    "model": "MiniMax-H3",
    "resolution": "2K",
    "ratio": "16:9",
    "shot": {
      "size": "medium-wide",
      "angle": "eye-level side view",
      "camera_motion": "fast tracking movement with small amplitude",
      "composition": "two opponents framed beside a dead tree at the cliff edge",
      "action_path": "the palm strike lands and the injured disciple hits the tree"
    },
    "dialogue": [],
    "image_inputs": [
      {
        "asset_id": "cliff-confrontation-r1",
        "h3_label": "Picture 1",
        "api_role": "reference_image",
        "purpose": "character identities, costumes, spacing, and cliff visual style",
        "source": "generate",
        "source_asset": null,
        "image_model": "Z-Image Turbo",
        "prompt": "一段完整、具体、自然的中文静帧生成提示词。",
        "parameters": {
          "width": 1280,
          "height": 720,
          "steps": 10,
          "cfg": 0,
          "seed": 2301
        }
      }
    ],
    "video_prompt": "subject_definitions:\n...\n\nsummary:\n...\n\nretention_analysis:\n...\n\ndetailed_description:\n...\n\noverall_soundscape:\n...\n\nnon_diegetic_music:\n..."
  }
]
```

## Layout

```text
NovelVideoPromptMaker/
├── README.md
├── screenplay-writer/
│   ├── SKILL.md
│   └── references/conventions.md
├── storyboard-prompt/
│   ├── SKILL.md
│   └── references/
│       ├── minimax-h3-video.md
│       ├── prompt-composition.md
│       └── z-image-turbo.md
└── examples/
    └── storyboard-prompt/
        └── xiakexing_episode_1.json
```

## Prompt example

[`examples/storyboard-prompt/xiakexing_episode_1.json`](examples/storyboard-prompt/xiakexing_episode_1.json)
adapts the supplied first-episode excerpt of *Xiakexing* into 51 source-grounded MiniMax-H3
pieces with colocated Z-Image prompts and H3 Ref2VA prompts.

## Installation

Copy or symlink the skill directories into the skill directory used by your agent:

```powershell
Copy-Item -Recurse .\screenplay-writer  "$env:USERPROFILE\.agents\skills\"
Copy-Item -Recurse .\storyboard-prompt  "$env:USERPROFILE\.agents\skills\"
```

## Provenance and license

Design adapted from the agent prompts of
[Stonewuu/ai-fusion-video](https://github.com/Stonewuu/ai-fusion-video) (MIT). This repository
contains original skill text and does not redistribute that project's code.
