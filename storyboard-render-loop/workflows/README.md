# Legacy LTX-2.3 FLF2V ComfyUI workflows (fp8)

These files are retained only for reproducibility of older runs. The active screenplay and
storyboard skills now target MiniMax-H3 and do not use these workflows. Use ComfyUI's native
MiniMax H3 T2V/I2V/R2V templates or the MiniMax API for new video generation.

Two ready-to-run **First-Last-Frame → Video** (FLF2V) workflows for LTX-2.3, wired for
the **fp8** diffusion checkpoint **and the fp8 Gemma-3 12B text encoder**. In the retired
LTX workflow, each adjacent pair in a keyframe chain produced one short clip. This behavior
is archival and must not guide new MiniMax-H3 prompts.

| File | Format | Use |
|------|--------|-----|
| `ltx23_flf2v_fp8_ui.json`  | ComfyUI **UI** graph | Drag-and-drop into the ComfyUI web canvas for interactive testing. |
| `ltx23_flf2v_fp8_api.json` | ComfyUI **API** prompt | `POST /prompt` for headless / scripted generation. |

Both default to **768×512, 97 frames, 24 fps** (a light, 24 GB-friendly test size).
`ltx23_flf2v_fp8_ui.json` is the official ComfyUI LTX-2.3 FLF2V template with the text
encoder retargeted to fp8 and the resolution/length lowered; it keeps the full parametric
UI (resolution/duration sliders) so you can tune it on the canvas.

## Why fp8 encoder (the 24 GB OOM fix)

LTX-2.3's text encoder is **Gemma-3 12B**. In bf16/fp16 it needs ~24–27 GB **by itself**,
which is what OOMs a 4090 even at 360p/20f (the diffusion pass is tiny; the encoder is the
bottleneck). These workflows load `gemma_3_12B_it_fp8_scaled.safetensors` (~12–13 GB).

Further VRAM relief if you still OOM:
- **Offload the encoder to CPU**: in the UI, set the *Load LTXV Audio Text Encoder* node's
  `device` to `cpu`; in the API file set `"device": "cpu"` on node `2`. Encoding runs once
  per prompt, so the CPU cost is a few seconds and it frees the encoder's whole footprint.
- **Even lighter encoder**: swap to `gemma_3_12B_it_fp4_mixed.safetensors` (the official
  default, smaller than fp8).
- Keep clips short (≤ ~97 frames) and use the distilled fp8 checkpoint (8-step schedule).

## Required models

| Role | File | Folder | Source |
|------|------|--------|--------|
| Diffusion (fp8, distilled) | `ltx-2.3-22b-distilled-fp8.safetensors` | `models/checkpoints/` | huggingface.co/Lightricks/LTX-2.3-fp8 |
| Text encoder (fp8) | `gemma_3_12B_it_fp8_scaled.safetensors` | `models/text_encoders/` | huggingface.co/Comfy-Org/ltx-2 → `split_files/text_encoders/` |

Both the checkpoint and the encoder loader also read the checkpoint for the audio VAE, so
the single fp8 checkpoint above is all you need on the model side. Update ComfyUI to the
latest version first (LTX-2.3 nodes are native — no custom nodes required).

## Using the UI workflow

1. Drag `ltx23_flf2v_fp8_ui.json` onto the ComfyUI canvas.
2. Load your two keyframes into **Load First Frame (K0)** and **Load Last Frame (Kn)**.
3. Put the per-segment motion prompt in the positive prompt; keep narration/dialogue you
   want spoken in the prompt text (LTX-2.3 generates audio natively).
4. (Optional) raise resolution/duration on the sliders once you confirm it fits VRAM.
5. Queue.

## Using the API workflow

`ltx23_flf2v_fp8_api.json` is a `/prompt`-format graph. Set the two input images
(`first_frame.png` / `last_frame.png` on nodes `7` and `8` — they must already exist in
ComfyUI's `input/` folder), edit the prompts on nodes `3`/`4`, the seed on node `17`, and
resolution/length on node `6` (and matching `frames_number`/`frame_rate` on node `14`),
then:

```bash
curl -X POST http://127.0.0.1:8188/prompt \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": $(cat ltx23_flf2v_fp8_api.json)}"
```

### Keep the two files in sync

The API file's input **names** are tied to your installed node versions. If ComfyUI ever
rejects a node input after an update, the authoritative fix is to load the UI file, enable
**Settings → Enable Dev Mode**, and use **Save (API Format)** to re-export — that
serialization always matches your exact nodes.

## Notes

- `length` must be `8·k + 1` (e.g. 97, 121, 161); `width`/`height` should be multiples of 32.
- The graph produces video **with audio** (native LTX-2.3). If you only need silent frames
  for the storyboard, ignore the audio track — the video still renders.
- This directory is about the *video* stage. Still-frame rendering (Z-Image Turbo) stays in
  `../scripts/comfy_zimage.py`.
