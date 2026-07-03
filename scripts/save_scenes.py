"""Save the scenes the agent wrote for one chapter into the project.

The agent decides scene boundaries and writes the prompts; this script just persists
them in a consistent, mappable layout and updates the manifest. Centralizing output
here keeps every scene file formatted identically and every chapter traceable.

Usage:
    python save_scenes.py --project PROJECT_DIR --chapter N --scenes scenes.json
    python save_scenes.py --project PROJECT_DIR --chapter N --scenes -   # read stdin

The input is either a JSON array of scenes, or an object that also carries the chapter's
cast for continuity planning:
    {
      "characters": [
        {"name": "Mira", "description": "woman in her 20s, dark hair tied back, patched red wool cloak"}
      ],
      "scenes": [ ... ]
    }

Each scene element:
    {
      "title": "Short scene label",
      "source_excerpt": "verbatim span of chapter text this clip depicts",
      "prompt": "single-paragraph LTX-2.3 positive prompt (with spoken lines in quotes)",
      "negative_prompt": "short, content-specific exclusions",   # optional
      "suggested_duration_seconds": 6,                           # optional, default 6
      "dialogue": [                                              # optional
        {"speaker": "Mira", "line": "I will come back."}
      ]
    }

Dialogue notes: LTX-2.3 speaks lines that appear in quotes inside the prompt, so the
agent should embed each dialogue line verbatim in the prompt. The structured "dialogue"
array is used to build a clean transcript and to check the line actually fits the clip.

Writes into the chapter directory:
    scenes.json            # canonical machine-readable list (edit + re-run to regenerate)
    scene-01.txt           # ready-to-paste positive prompt
    scene-01.negative.txt  # negative prompt
    scene-02.txt ...
    transcript.txt         # spoken lines per scene (speaker: line) if any dialogue exists
updates manifest.json (scene_count, status="generated"), and maintains a project-level
characters.json cast sheet so a character stays visually consistent across chapters.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import dump_json, estimate_speech_seconds, load_json, word_count  # noqa: E402

DEFAULT_NEGATIVE = (
    "text overlay, subtitles, watermark, warped hands, extra fingers, "
    "static frozen frame, blurry"
)


def _find_chapter(manifest: dict, number: int) -> dict:
    for c in manifest["chapters"]:
        if c["number"] == number:
            return c
    raise SystemExit(f"ERROR: chapter {number} not found in manifest.")


def _load_payload(path: str):
    """Return (scenes, characters). Accepts a bare scenes array, or an object
    {"characters": [...], "scenes": [...]} for holistic chapter planning."""
    raw = sys.stdin.read() if path == "-" else None
    data = json.loads(raw) if raw is not None else load_json(path)
    characters = []
    if isinstance(data, dict):
        characters = data.get("characters") or []
        data = data.get("scenes", data)
    if not isinstance(data, list) or not data:
        raise SystemExit("ERROR: scenes input must be a non-empty JSON array (or an "
                         "object with a non-empty 'scenes' array).")
    return data, characters


def _normalize_characters(raw) -> list:
    """Normalize a cast sheet: [{name, description}] with fixed visual descriptions."""
    out = []
    for c in raw or []:
        if isinstance(c, str):
            name, desc = c.strip(), ""
        else:
            name = str(c.get("name", "")).strip()
            desc = str(c.get("description", c.get("desc", ""))).strip()
        if name:
            out.append({"name": name, "description": desc})
    return out


def _merge_project_cast(project_dir: str, chapter_number: int, characters: list) -> list:
    """Accumulate a project-wide cast sheet so a character looks the same across chapters.

    Keeps the first description seen for each name (the canonical look) and records which
    chapters use them; flags when a later chapter supplies a different description.
    """
    path = os.path.join(project_dir, "characters.json")
    registry = load_json(path).get("characters", []) if os.path.isfile(path) else []
    by_name = {c["name"]: c for c in registry}
    notes = []
    for c in characters:
        entry = by_name.get(c["name"])
        if entry is None:
            entry = {"name": c["name"], "description": c["description"], "chapters": []}
            by_name[c["name"]] = entry
            registry.append(entry)
        elif c["description"] and entry["description"] and c["description"] != entry["description"]:
            notes.append(f"character '{c['name']}' description differs from chapter "
                         f"{entry['chapters']}; keeping the original for continuity")
        if chapter_number not in entry["chapters"]:
            entry["chapters"].append(chapter_number)
    dump_json(path, {"characters": registry})
    return notes


def _normalize_dialogue(raw) -> list:
    """Accept a list of {speaker, line} dicts, or bare strings, or a single string."""
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [raw]
    out = []
    for d in raw:
        if isinstance(d, str):
            speaker, line = "", d.strip()
        else:
            speaker = str(d.get("speaker", "")).strip()
            line = str(d.get("line", d.get("text", ""))).strip()
        if line:
            out.append({"speaker": speaker, "line": line})
    return out


def _line_in_prompt(line: str, prompt: str) -> bool:
    """True if the spoken line appears in the prompt (ignoring surrounding quotes/space)."""
    def norm(t: str) -> str:
        t = re.sub(r'["""«»「」『』]', "", t)
        return re.sub(r"\s+", " ", t).strip().lower()
    return norm(line) in norm(prompt)


def _speech_clause(speaker: str, line: str) -> str:
    """Build a natural 'X says "…"' clause in the language of the line/speaker.

    Used only as a fallback when the agent didn't weave a spoken line into the prompt.
    Matching the script keeps a native-language prompt from getting an English graft.
    """
    sample = (speaker or "") + line
    if re.search(r"[\u3040-\u30ff]", sample):          # Japanese kana present
        who = speaker or "声"
        return f"{who}は言う：「{line}」"
    if re.search(r"[\u4e00-\u9fff\u3400-\u4dbf]", sample):  # Chinese (no kana)
        who = speaker or "画外音"
        return f"{who}说：“{line}”"
    who = speaker or "A voice"
    return f'{who} says, "{line}".'


def _embed_dialogue(prompt: str, dialogue: list) -> tuple:
    """Guarantee every spoken line is present verbatim in the prompt.

    LTX-2.3 only voices lines that appear (in quotes) inside the single main prompt, so
    any dialogue line the agent didn't already weave in is appended as a natural speech
    clause in the line's own language. Returns (prompt, list_of_added_lines).
    """
    added = []
    for d in dialogue:
        line = d["line"]
        if _line_in_prompt(line, prompt):
            continue
        prompt = prompt.rstrip()
        if prompt and prompt[-1] not in ".!?。！？\"'”」":
            prompt += "."
        prompt += " " + _speech_clause(d["speaker"], line)
        added.append(line)
    return prompt, added


def main() -> int:
    ap = argparse.ArgumentParser(description="Persist a chapter's scenes into the project.")
    ap.add_argument("--project", required=True, help="Project dir (contains manifest.json)")
    ap.add_argument("--chapter", required=True, type=int, help="Chapter number")
    ap.add_argument("--scenes", required=True, help="Path to scenes JSON, or '-' for stdin")
    args = ap.parse_args()

    manifest_path = os.path.join(args.project, "manifest.json")
    if not os.path.isfile(manifest_path):
        raise SystemExit(f"ERROR: manifest not found: {manifest_path}")
    manifest = load_json(manifest_path)
    chapter = _find_chapter(manifest, args.chapter)
    ch_dir = os.path.join(args.project, chapter["dir"])
    if not os.path.isdir(ch_dir):
        raise SystemExit(f"ERROR: chapter directory missing: {ch_dir}")

    scenes_in, characters_in = _load_payload(args.scenes)
    characters = _normalize_characters(characters_in)

    # Clear previous scene-*.txt and transcript so stale content doesn't linger.
    for name in os.listdir(ch_dir):
        if (name.startswith("scene-") and name.endswith((".txt", ".negative.txt"))) \
                or name == "transcript.txt":
            os.remove(os.path.join(ch_dir, name))

    canonical = []
    warnings = []
    transcript_lines = []
    for i, s in enumerate(scenes_in, start=1):
        prompt = str(s.get("prompt", "")).strip()
        if not prompt:
            raise SystemExit(f"ERROR: scene {i} has an empty prompt.")
        excerpt = str(s.get("source_excerpt", "")).strip()
        if not excerpt:
            warnings.append(f"scene {i}: no source_excerpt (mapping back to novel will be weak)")
        neg = str(s.get("negative_prompt", "")).strip() or DEFAULT_NEGATIVE
        try:
            dur = int(s.get("suggested_duration_seconds", 6) or 6)
        except (TypeError, ValueError):
            dur = 6

        # Integrate any spoken lines into the single main prompt — LTX-2.3 has no
        # separate transcript input, so a line only gets voiced if it's in the prompt.
        dialogue = _normalize_dialogue(s.get("dialogue"))
        prompt, added = _embed_dialogue(prompt, dialogue)
        if added:
            warnings.append(
                f"scene {i}: auto-embedded {len(added)} dialogue line(s) into the prompt "
                f"(they weren't woven in). Review scene-{i:02d}.txt for phrasing.")

        wc = word_count(prompt)
        if wc > 200:
            warnings.append(f"scene {i}: prompt is {wc} words (>200); consider trimming")

        speech_secs = sum(estimate_speech_seconds(d["line"]) for d in dialogue)
        if dialogue and speech_secs > dur:
            warnings.append(
                f"scene {i}: dialogue needs ~{speech_secs:.1f}s but clip is {dur}s; "
                f"shorten the line or raise suggested_duration_seconds")

        stem = f"scene-{i:02d}"
        with open(os.path.join(ch_dir, f"{stem}.txt"), "w", encoding="utf-8") as fh:
            fh.write(prompt + "\n")
        with open(os.path.join(ch_dir, f"{stem}.negative.txt"), "w", encoding="utf-8") as fh:
            fh.write(neg + "\n")

        if dialogue:
            transcript_lines.append(f"## Scene {i:02d} — {str(s.get('title','')).strip()} "
                                    f"[{dur}s clip, ~{speech_secs:.1f}s speech]")
            for d in dialogue:
                who = d["speaker"] or "—"
                transcript_lines.append(f"  {who}: {d['line']}")
            transcript_lines.append("")

        canonical.append({
            "index": i,
            "title": str(s.get("title", "")).strip() or f"Scene {i}",
            "source_excerpt": excerpt,
            "prompt": prompt,
            "negative_prompt": neg,
            "suggested_duration_seconds": dur,
            "dialogue": dialogue,
            "estimated_speech_seconds": round(speech_secs, 1),
            "prompt_word_count": wc,
            "files": {"prompt": f"{stem}.txt", "negative": f"{stem}.negative.txt"},
        })

    dump_json(os.path.join(ch_dir, "scenes.json"), {
        "chapter_number": chapter["number"],
        "chapter_title": chapter["title"],
        "characters": characters,
        "scene_count": len(canonical),
        "scenes": canonical,
    })

    cast_notes = _merge_project_cast(args.project, chapter["number"], characters)

    if transcript_lines:
        header = (f"# Transcript — Chapter {chapter['number']}: {chapter['title']}\n"
                  f"# Reference/subtitle copy for review. LTX-2.3 reads the spoken lines\n"
                  f"# from inside each scene-NN.txt prompt, NOT from this file.\n")
        with open(os.path.join(ch_dir, "transcript.txt"), "w", encoding="utf-8") as fh:
            fh.write(header + "\n" + "\n".join(transcript_lines).rstrip() + "\n")

    chapter["scene_count"] = len(canonical)
    chapter["status"] = "generated"
    dump_json(manifest_path, manifest)

    print(f"Saved {len(canonical)} scene(s) for chapter {chapter['number']} -> {ch_dir}")
    if characters:
        print(f"  cast: {len(characters)} character(s) recorded -> characters.json")
    with_dialogue = sum(1 for c in canonical if c["dialogue"])
    print(f"  dialogue coverage: {with_dialogue}/{len(canonical)} scene(s) have a spoken line")
    if transcript_lines:
        print(f"  transcript.txt written ({sum(len(c['dialogue']) for c in canonical)} spoken line(s))")
    silent = [c["index"] for c in canonical if not c["dialogue"]]
    if silent:
        print(f"  NOTE: no dialogue in scene(s) {silent} — add a spoken line unless truly impossible")
    for n in cast_notes:
        print(f"  NOTE: {n}")
    for w in warnings:
        print(f"  WARNING: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
