"""Validate a generated project and report what needs regeneration.

Use this after generating scenes (or any time you edit scenes.json by hand) to catch
problems before you feed prompts into LTX-2.3. It reports per chapter and exits non-zero
if any errors are found, so it can gate a batch workflow.

Usage:
    python validate.py --project PROJECT_DIR [--strict]

Checks per scene:
    - prompt is non-empty and <= 200 words (LTX-2.3 degrades past ~200)
    - negative_prompt present
    - source_excerpt present AND actually found in the chapter source (mapping integrity)
    - duration within 3-20 s
Checks per chapter:
    - status == generated and scenes.json exists

--strict promotes warnings (e.g. weak excerpt match) to errors.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import estimate_speech_seconds, load_json, read_text, word_count  # noqa: E402


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _line_in_prompt(line: str, prompt: str) -> bool:
    strip = lambda t: re.sub(r"\s+", " ", re.sub(r'["""«»「」『』]', "", t or "")).strip().lower()
    return strip(line) in strip(prompt)


def _excerpt_matches(excerpt: str, source_norm: str) -> bool:
    """True if the excerpt maps back to the chapter (exact or strong token overlap)."""
    ex = _normalize(excerpt)
    if not ex:
        return False
    if ex in source_norm:
        return True
    # Fall back to token coverage: excerpts may be lightly paraphrased/trimmed.
    tokens = [t for t in re.findall(r"\w+", ex) if len(t) > 3]
    if not tokens:
        return False
    hits = sum(1 for t in tokens if t in source_norm)
    return hits / len(tokens) >= 0.6


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a NovelVideoPromptMaker project.")
    ap.add_argument("--project", required=True, help="Project dir (contains manifest.json)")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = ap.parse_args()

    manifest = load_json(os.path.join(args.project, "manifest.json"))
    errors, warnings = [], []
    total_scenes = 0
    scenes_with_dialogue = 0

    for ch in manifest["chapters"]:
        tag = f"Ch {ch['number']} ({ch['title'][:40]})"
        ch_dir = os.path.join(args.project, ch["dir"])
        scenes_path = os.path.join(ch_dir, "scenes.json")
        if ch["status"] != "generated" or not os.path.isfile(scenes_path):
            warnings.append(f"{tag}: no scenes generated yet")
            continue

        source_norm = _normalize(read_text(os.path.join(ch_dir, "source.txt")))
        scenes = load_json(scenes_path).get("scenes", [])
        if not scenes:
            errors.append(f"{tag}: scenes.json has no scenes")
            continue

        for s in scenes:
            total_scenes += 1
            sid = f"{tag} scene {s.get('index')}"
            prompt = str(s.get("prompt", "")).strip()
            if not prompt:
                errors.append(f"{sid}: empty prompt")
            elif word_count(prompt) > 200:
                warnings.append(f"{sid}: prompt {word_count(prompt)} words (>200)")
            if not str(s.get("negative_prompt", "")).strip():
                warnings.append(f"{sid}: no negative prompt")
            dur = s.get("suggested_duration_seconds", 6)
            if not isinstance(dur, int) or not (3 <= dur <= 20):
                warnings.append(f"{sid}: duration {dur}s outside 3-20s range")
            excerpt = str(s.get("source_excerpt", "")).strip()
            if not excerpt:
                warnings.append(f"{sid}: missing source_excerpt (can't map back to novel)")
            elif not _excerpt_matches(excerpt, source_norm):
                warnings.append(f"{sid}: source_excerpt not found in chapter (mapping suspect)")

            dialogue = s.get("dialogue") or []
            if dialogue:
                scenes_with_dialogue += 1
            speech = sum(estimate_speech_seconds(d.get("line", "")) for d in dialogue)
            for d in dialogue:
                line = str(d.get("line", "")).strip()
                if line and not _line_in_prompt(line, prompt):
                    errors.append(f"{sid}: dialogue not embedded in prompt, won't be spoken: \"{line[:30]}\"")
            if dialogue and isinstance(dur, int) and speech > dur:
                warnings.append(f"{sid}: dialogue ~{speech:.1f}s exceeds {dur}s clip (may cut off)")

    if args.strict:
        errors.extend(warnings)
        warnings = []

    cov = f"{scenes_with_dialogue}/{total_scenes}" if total_scenes else "0/0"
    print(f"Project: {manifest.get('novel')}  |  chapters: {len(manifest['chapters'])}  "
          f"|  scenes: {total_scenes}  |  dialogue coverage: {cov}")
    if total_scenes and scenes_with_dialogue < total_scenes:
        print(f"  NOTE: {total_scenes - scenes_with_dialogue} scene(s) have no spoken line; "
              f"add dialogue unless a scene truly can't have any.")
    for w in warnings:
        print(f"  WARNING: {w}")
    for e in errors:
        print(f"  ERROR:   {e}")
    if errors:
        print(f"\nFAILED with {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"\nOK — {len(warnings)} warning(s), no errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
