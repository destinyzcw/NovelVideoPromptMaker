"""Render a generated project's scene prompts into LTX-2.3 video clips with Draw Things.

This is the "last mile": once the agent has written a project's chapter JSON files (and
`validate.py` is happy), this script drives the **Draw Things CLI** (`draw-things-cli
generate`) to turn every scene's prompt into an actual video clip — one `.mp4`/`.mov`
per scene, with LTX-2.3's synchronized **audio and spoken dialogue** muxed in.

Why the CLI and not the HTTP API: Draw Things' HTTP API (`/sdapi/v1/txt2img`) returns
only image frames in its JSON `images` array — it carries no audio track. Since this
skill embeds a spoken line in (nearly) every prompt, we use `draw-things-cli generate`,
which retrieves the model's audio alongside the frames and writes a real video file.

    Requirements (run on the machine where Draw Things / its models live, e.g. your Mac):
      - draw-things-cli  (brew install --HEAD drawthingsai/draw-things/draw-things-cli)
      - ffmpeg  (optional) — only needed to chain `continuation` scenes seamlessly by
        seeding the next clip with the previous clip's last frame (image-to-video).

Usage:
    # Preview every command without generating anything:
    python render_videos.py --project output/the-lantern-road \
        --model ltx_2.3_22b_distilled_q6p.ckpt --dry-run

    # Render the whole project (skips clips already rendered):
    python render_videos.py --project output/the-lantern-road \
        --model ltx_2.3_22b_distilled_q6p.ckpt

    # Just one chapter, first 2 scenes, to sanity-check settings first:
    python render_videos.py --project output/the-lantern-road \
        --model ltx_2.3_22b_distilled_q6p.ckpt --chapter 1 --limit 2

Output:
    <project>/videos/ch001-scene01.mp4, ch001-scene02.mp4, ...
    <project>/videos/render-manifest.json   (what was rendered, with the exact command)

Clip length / frame count:
    LTX-2.3 runs at ~24 fps and requires a frame count of the form 8k+1. Each scene's
    `suggested_duration_seconds` is converted to frames = round(duration * fps) snapped to
    the nearest 8k+1 and capped at 201 (the model/CLI maximum, ~8 s). Longer stretches of
    story are meant to be split across scenes in the JSON, not forced into one clip.

Chaining (`continuation: true`):
    A continuation scene opens from the previous clip's final frame. If ffmpeg is
    available, this script extracts the previous clip's last frame and passes it to the
    CLI as `--image` (image-to-video) at `--continuation-strength`, so the character's
    look carries over pixel-for-pixel across the seam. Without ffmpeg, the scene is
    rendered as plain text-to-video and a warning is printed.

The script never edits the chapter JSON; it only reads it and writes video files.
Standard library only — no third-party Python dependencies.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import RECOMMENDED_PARAMS, enable_utf8_stdout, load_json  # noqa: E402

# LTX-2.3 hard limit: the CLI accepts num_frames in 1...201 (see Parameters.swift).
MAX_FRAMES = 201
# Video containers we know how to write, mapped to a default codec for --video-format.
_MP4_CODEC = "h264"   # .mp4 -> H.264 (hevc also valid); ProRes requires .mov
_MOV_CODEC = "prores422hq"

# Common resolution presets -> (width, height), already snapped to multiples of 64.
RESOLUTION_PRESETS = {
    "720p": (1280, 704),
    "720p-portrait": (704, 1280),
    "1080p": (1920, 1088),
    "1080p-portrait": (1088, 1920),
    "512": (512, 512),
}


def snap_frames(duration_seconds: float, fps: int) -> int:
    """Convert a clip duration to an LTX-2.3-legal frame count (nearest 8k+1, capped)."""
    raw = max(1, round(float(duration_seconds) * fps))
    k = max(1, round((raw - 1) / 8))
    frames = 8 * k + 1
    return max(9, min(frames, MAX_FRAMES))


def snap_dim(value: int) -> int:
    """Round a pixel dimension down to a multiple of 64 (LTX-2.3 wants 32/64 multiples)."""
    return max(64, (int(value) // 64) * 64)


def resolve_size(args) -> tuple[int, int]:
    """Decide output width/height from --width/--height or a --resolution preset."""
    if args.width and args.height:
        return snap_dim(args.width), snap_dim(args.height)
    preset = RESOLUTION_PRESETS.get(args.resolution, RESOLUTION_PRESETS["720p"])
    width = snap_dim(args.width) if args.width else preset[0]
    height = snap_dim(args.height) if args.height else preset[1]
    return width, height


def video_format_for(output_path: Path, override: str | None) -> str:
    """Pick a --video-format value matching the output container (or honor override)."""
    if override:
        return override
    return _MOV_CODEC if output_path.suffix.lower() == ".mov" else _MP4_CODEC


def extract_last_frame(ffmpeg: str, video_path: Path, out_png: Path) -> bool:
    """Grab the final frame of a rendered clip into a PNG (for continuation i2v).

    Returns True on success. Uses a short seek from the end of file, which is robust
    without having to know the exact frame count.
    """
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-nostdin", "-loglevel", "error",
        "-sseof", "-0.35", "-i", str(video_path),
        "-update", "1", "-frames:v", "1", str(out_png),
    ]
    try:
        subprocess.run(cmd, check=True)
        return out_png.is_file()
    except (subprocess.CalledProcessError, OSError):
        return False


def build_command(cli: str, *, model: str, prompt: str, negative: str, frames: int,
                  width: int, height: int, steps: int, cfg: float, seed: int | None,
                  output: Path, video_format: str, init_image: Path | None,
                  strength: float, models_dir: str | None, config_json: str | None,
                  no_negative: bool, extra: list[str]) -> list[str]:
    """Assemble a `draw-things-cli generate` argv for one scene."""
    cmd = [cli, "generate", "--model", model, "--prompt", prompt]
    if negative and not no_negative:
        cmd += ["--negative-prompt", negative]
    cmd += [
        "--frames", str(frames),
        "--width", str(width),
        "--height", str(height),
        "--steps", str(steps),
        "--cfg", str(cfg),
        "--output", str(output),
        "--video-format", video_format,
    ]
    if seed is not None:
        cmd += ["--seed", str(seed)]
    if init_image is not None:
        cmd += ["--image", str(init_image), "--strength", str(strength)]
    if models_dir:
        cmd += ["--models-dir", models_dir]
    if config_json:
        cmd += ["--config-json", config_json]
    cmd += extra
    return cmd


def iter_scenes(project: Path):
    """Yield (chapter_dict, chapter_doc, scene) for every scene, in manifest order."""
    manifest = load_json(project / "manifest.json")
    for ch in manifest.get("chapters", []):
        if ch.get("status") != "generated":
            continue
        chapter_path = project / ch["file"]
        if not chapter_path.is_file():
            continue
        doc = load_json(chapter_path)
        scenes = sorted(doc.get("scenes", []), key=lambda s: s.get("index", 0))
        for scene in scenes:
            yield ch, doc, scene


def main() -> int:
    enable_utf8_stdout()
    rp = RECOMMENDED_PARAMS
    ap = argparse.ArgumentParser(
        description="Render a project's scene prompts to LTX-2.3 clips via draw-things-cli.")
    ap.add_argument("--project", required=True, help="Project dir (contains manifest.json)")
    ap.add_argument("--model", required=True,
                    help="LTX-2 checkpoint filename as it appears in Draw Things models dir")
    ap.add_argument("--out", default=None,
                    help="Output dir for clips (default: <project>/videos)")
    ap.add_argument("--chapter", type=int, default=None, help="Only render this chapter number")
    ap.add_argument("--scene", type=int, default=None, help="Only render this scene index")
    ap.add_argument("--limit", type=int, default=None, help="Render at most N clips (testing)")
    ap.add_argument("--container", choices=["mp4", "mov"], default="mp4",
                    help="Output container (mp4=H.264, mov=ProRes). Default mp4.")
    ap.add_argument("--video-format", default=None,
                    help="Override --video-format (prores4444/prores422hq/h264/hevc)")

    ap.add_argument("--fps", type=int, default=rp["fps"], help=f"Frames per second (default {rp['fps']})")
    ap.add_argument("--steps", type=int, default=rp["sampling_steps"],
                    help=f"Sampling steps (default {rp['sampling_steps']}; distilled models ~12)")
    ap.add_argument("--cfg", type=float, default=rp["video_cfg"],
                    help=f"CFG guidance scale (default {rp['video_cfg']}; distilled models ~1.0)")
    ap.add_argument("--resolution", default=rp["resolution"],
                    help="Preset: 720p, 720p-portrait, 1080p, 1080p-portrait, 512 (default 720p)")
    ap.add_argument("--width", type=int, default=None, help="Override width (snapped to x64)")
    ap.add_argument("--height", type=int, default=None, help="Override height (snapped to x64)")
    ap.add_argument("--seed", type=int, default=None,
                    help="Base seed; each clip uses seed+offset for reproducible-but-distinct noise")
    ap.add_argument("--no-negative", action="store_true",
                    help="Ignore negative prompts (use for distilled models run at cfg ~1.0)")
    ap.add_argument("--config-json", default=None,
                    help="Raw JSON string merged into the CLI config (advanced; e.g. audio cfg)")

    ap.add_argument("--continuation-strength", type=float, default=0.7,
                    help="img2img strength for continuation scenes seeded by prev last frame")
    ap.add_argument("--no-chain", action="store_true",
                    help="Do not seed continuation scenes from the previous clip's last frame")

    ap.add_argument("--cli", default="draw-things-cli", help="Path to the draw-things-cli binary")
    ap.add_argument("--ffmpeg", default="ffmpeg", help="Path to ffmpeg (for continuation chaining)")
    ap.add_argument("--models-dir", default=None, help="Override Draw Things models directory")
    ap.add_argument("--extra", nargs=argparse.REMAINDER, default=[],
                    help="Everything after --extra is passed verbatim to draw-things-cli")

    ap.add_argument("--skip-existing", action="store_true", default=True,
                    help="Skip scenes whose output file already exists (default on)")
    ap.add_argument("--overwrite", dest="skip_existing", action="store_false",
                    help="Re-render even if the output file exists")
    ap.add_argument("--dry-run", action="store_true", help="Print commands; do not run them")
    args = ap.parse_args()

    project = Path(args.project)
    if not (project / "manifest.json").is_file():
        print(f"ERROR: {project}/manifest.json not found", file=sys.stderr)
        return 2

    out_dir = Path(args.out) if args.out else project / "videos"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / ".frames"  # scratch for continuation last-frames

    ext = "." + args.container
    ffmpeg = shutil.which(args.ffmpeg) if not args.dry_run else args.ffmpeg
    chain = not args.no_chain
    if chain and not args.dry_run and not ffmpeg:
        print("NOTE: ffmpeg not found — continuation scenes will render as plain "
              "text-to-video (no last-frame seam). Install ffmpeg to enable chaining.")

    records = []
    rendered = failed = skipped = 0
    prev_output_by_chapter: dict[int, Path] = {}

    for ch, doc, scene in iter_scenes(project):
        cnum = ch["number"]
        idx = scene.get("index")
        if args.chapter is not None and cnum != args.chapter:
            continue
        if args.scene is not None and idx != args.scene:
            continue

        prompt = str(scene.get("prompt", "")).strip()
        if not prompt:
            print(f"SKIP  ch{cnum:03d} scene {idx}: empty prompt")
            continue

        width, height = resolve_size(args)
        frames = snap_frames(scene.get("suggested_duration_seconds", rp["frames"] / args.fps),
                             args.fps)
        output = out_dir / f"ch{cnum:03d}-scene{int(idx):02d}{ext}"
        seed = None if args.seed is None else args.seed + cnum * 100 + int(idx)

        # Continuation: seed this clip from the previous scene's last frame (image-to-video).
        init_image = None
        prev = prev_output_by_chapter.get(cnum)
        if chain and scene.get("continuation") and prev is not None:
            seed_png = frames_dir / f"ch{cnum:03d}-scene{int(idx):02d}-seed.png"
            if args.dry_run:
                # Predecessor isn't rendered during a dry-run, so just show the seam.
                init_image = seed_png
            elif not prev.is_file():
                print(f"  WARNING: predecessor {prev.name} not found; "
                      f"rendering scene {idx} as text-to-video")
            elif not ffmpeg:
                pass  # ffmpeg missing was already reported once up front
            elif extract_last_frame(ffmpeg, prev, seed_png):
                init_image = seed_png
            else:
                print(f"  WARNING: could not extract last frame from {prev.name}; "
                      f"rendering scene {idx} as text-to-video")

        cmd = build_command(
            args.cli, model=args.model, prompt=prompt,
            negative=str(scene.get("negative_prompt", "")).strip(),
            frames=frames, width=width, height=height, steps=args.steps, cfg=args.cfg,
            seed=seed, output=output, video_format=video_format_for(output, args.video_format),
            init_image=init_image, strength=args.continuation_strength,
            models_dir=args.models_dir, config_json=args.config_json,
            no_negative=args.no_negative, extra=args.extra or [])

        label = f"ch{cnum:03d} scene {idx} [{frames}f @ {width}x{height}]"
        # Track predecessor for the *next* scene's potential continuation, regardless of skip.
        prev_output_by_chapter[cnum] = output

        if args.skip_existing and output.is_file() and not args.dry_run:
            print(f"SKIP  {label}: {output.name} exists (use --overwrite to redo)")
            skipped += 1
            continue

        if args.dry_run:
            print(f"DRY   {label}\n      {_render_cmd(cmd)}")
            records.append({"chapter": cnum, "scene": idx, "output": str(output),
                            "frames": frames, "command": cmd})
            rendered += 1
            if args.limit and rendered >= args.limit:
                break
            continue

        print(f"RENDER {label} -> {output.name}")
        try:
            subprocess.run(cmd, check=True)
            status = "ok"
            rendered += 1
        except FileNotFoundError:
            print(f"ERROR: '{args.cli}' not found. Install draw-things-cli or pass --cli PATH.",
                  file=sys.stderr)
            return 2
        except subprocess.CalledProcessError as exc:
            print(f"  FAILED: draw-things-cli exited {exc.returncode}")
            status = f"failed:{exc.returncode}"
            failed += 1

        records.append({"chapter": cnum, "scene": idx, "output": str(output),
                        "frames": frames, "width": width, "height": height,
                        "seed": seed, "status": status, "command": cmd})
        _write_manifest(out_dir, project, args, records)  # incremental so progress survives

        if args.limit and (rendered + failed) >= args.limit:
            break

    if args.dry_run:
        _write_manifest(out_dir, project, args, records)

    print(f"\nDone. rendered={rendered} skipped={skipped} failed={failed}  ->  {out_dir}")
    return 1 if failed else 0


def _render_cmd(cmd: list[str]) -> str:
    """Human-readable, copy-pasteable rendering of an argv (quotes args with spaces)."""
    out = []
    for a in cmd:
        out.append(f'"{a}"' if (" " in a or "\n" in a or '"' in a) else a)
    return " ".join(out)


def _write_manifest(out_dir: Path, project: Path, args, records: list) -> None:
    manifest = {
        "project": str(project),
        "model": args.model,
        "backend": "draw-things-cli (local)",
        "fps": args.fps,
        "steps": args.steps,
        "cfg": args.cfg,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dry_run": args.dry_run,
        "clips": records,
    }
    (out_dir / "render-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
