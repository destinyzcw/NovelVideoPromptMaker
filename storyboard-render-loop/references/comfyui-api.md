# ComfyUI Z-Image Turbo — API notes

The render loop talks to ComfyUI over its HTTP API. The ComfyUI server usually
runs on a **separate GPU box on the same LAN** — you do not run it on the agent
machine. Set `COMFYUI_HOST` to that box, e.g. `http://192.168.1.50:8188`. (For how
to start ComfyUI and expose it on the LAN, see the repo README's "Setup" section —
that's a one-time manual step done on the GPU box, not something the skill does.)

## Endpoints used

| Method | Path | Purpose |
|---|---|---|
| POST | `/prompt` | Queue a job. Body: `{"prompt": <api-workflow>, "client_id": "<uuid>"}`. Returns `{"prompt_id": "..."}`. |
| GET | `/history/{prompt_id}` | Poll job status + outputs. When done, `outputs.<node>.images[]` lists produced files. |
| GET | `/view?filename=&subfolder=&type=output` | Download a produced image. |

`scripts/comfy_zimage.py` wraps all three. It patches the workflow, submits,
polls `/history` until outputs appear, downloads the first image to `--out`.

## The workflow JSON: two formats

ComfyUI has two JSON formats and they are NOT interchangeable:

- **UI format** (`Workflow -> Export`): has a top-level `"nodes"` array with
  positions/links. The API rejects this. The script detects it and errors.
- **API format** (`Workflow -> Export (API)`, needs dev mode enabled in
  ComfyUI settings): a flat `{ "<node_id>": {"class_type":..., "inputs":{...}} }`
  map. THIS is what `/prompt` wants and what the script patches.

The bundled `scripts/zimage_workflow.api.json` is a ready API-format graph for
the standard Z-Image Turbo setup, mirroring the official Comfy-Org template:

```
UNETLoader(z_image_turbo_bf16) ─┐
CLIPLoader(qwen_3_4b, type=lumina2) → CLIPTextEncode(positive) ─┐
                                        └→ ConditioningZeroOut(negative)
EmptySD3LatentImage(1024x1024) ───────────────────────────────→ KSampler ─→ VAEDecode ─→ SaveImage
VAELoader(ae) ────────────────────────────────────────────────────────────┘
```

KSampler defaults: `steps 8`, `cfg 1.0`, `sampler euler`, `scheduler simple`,
`denoise 1.0`. (Z-Image Turbo is distilled; guidance is effectively off, so the
negative branch is a `ConditioningZeroOut` of the positive — negative text does
nothing. Keep exclusions in the positive prompt.)

If your ComfyUI has different model filenames or a customized graph, export your
own working graph via **Export (API)** and pass it with `--workflow`. The script
finds nodes structurally (by following the sampler's links and by class_type),
so most custom graphs work without edits. To force-target a node, set its
`_meta.title` in ComfyUI to one of: `POSITIVE_PROMPT`, `NEGATIVE_PROMPT`,
`LATENT_IMAGE`, `SAMPLER`, `SAVE_IMAGE`.

## Required model files on the ComfyUI box

```
ComfyUI/models/text_encoders/qwen_3_4b.safetensors
ComfyUI/models/diffusion_models/z_image_turbo_bf16.safetensors   (or fp8 variant)
ComfyUI/models/vae/ae.safetensors
```
Source: `huggingface.co/Comfy-Org/z_image_turbo` (split_files/).

## CLI quick reference

```
python scripts/comfy_zimage.py \
  --host http://192.168.1.50:8188 \
  --prompt "电影感全景，..." \
  --seed 12345 --steps 9 --cfg 1.0 --width 1280 --height 720 \
  --filename-prefix shot_2-3-05 \
  --out ./renders/2-3-05.png
```

- `--seed` omitted → random seed (printed in the JSON result so you can pin it).
- `--cfg` omitted → keep the workflow's value (1.0). Z-Image Turbo wants ~1.0.
- `--dry-run` → patch and print the workflow + a `patch_report` without
  submitting. Use this once after pointing at a new workflow to confirm every
  field (positive/seed/steps/size/filename) resolved to `true`.
- Result line is JSON: `{"status":"ok","seed":...,"out":"...","images":[...]}`
  on success (exit 0); `{"status":"error","error":"..."}` on failure (exit 1).

## Troubleshooting

- **`cannot reach ComfyUI`** — wrong `COMFYUI_HOST`, box asleep, or firewall.
  Verify with `curl http://<host>:8188/system_stats` from the agent machine.
- **`workflow looks like a UI export`** — you exported the wrong format; use
  Export (API).
- **`could not locate a positive prompt node`** — your graph nests the prompt
  oddly; tag the CLIPTextEncode with `_meta.title = POSITIVE_PROMPT`.
- **Blank / wrong model errors from ComfyUI** — model filenames in the workflow
  don't match files on the box; fix `unet_name` / `clip_name` / `vae_name` in
  your exported workflow.
