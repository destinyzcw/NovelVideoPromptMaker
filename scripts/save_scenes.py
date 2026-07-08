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
      "continuation": false,                                     # optional, default false
      "end_state": "how this clip's final frame looks",          # optional
      "dialogue": [                                              # optional
        {"speaker": "Mira", "line": "I will come back."}
      ]
    }

Stitching / continuity fields: because a long sequence is rendered as several short
clips and stitched, set "continuation": true on a scene that must begin exactly where
the previous scene ended. DrawThings renders it image-to-video from the previous clip's
last frame natively (its "use last frame" carry-over) — the skill no longer extracts
frames itself. Give every scene that FEEDS a continuation an "end_state" describing its
final frame (pose, framing, lighting) so the continuation prompt can open from it and so
the model knows how to finish the feeding clip's motion. A continuation prompt should
open from that frozen state and describe the onward motion rather than re-establishing
the whole scene. Because the carried frame already fixes the character's look, a
continuation clip can keep its restated appearance anchors light.

Dialogue notes: LTX-2.3 speaks lines that appear in quotes inside the prompt, so the
agent should embed each dialogue line verbatim in the prompt. The structured "dialogue"
array is used to render the dialogue summary and to check the line actually fits the clip.

Fills the chapter's flat JSON file in place:
    chapter-NNN-<slug>.json  # source_text is preserved; characters + scenes are added.
                             #   Each scene carries its positive prompt, negative prompt,
                             #   dialogue, duration, and continuity fields.
It also updates manifest.json (scene_count, status="generated") and maintains a
project-level characters.json cast sheet so a character stays visually consistent
across chapters.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    default_negative,
    dump_json,
    enable_utf8_stdout,
    estimate_speech_seconds,
    is_cjk,
    load_json,
    word_count,
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


def _appearance_anchors(description: str) -> list:
    """Split a character's canonical look into individual visual anchors.

    A cast-sheet description is a list of concrete traits separated by CJK/Latin commas
    or slashes ("短黑发、粗布深衣、提旧马灯" / "dark hair, red cloak, brass lantern"). Each
    piece is an anchor that should reappear, worded identically, in every prompt the
    character is in — paraphrasing or dropping anchors is what makes a look drift.
    """
    parts = re.split(r"[，,、;；/／]+", description or "")
    return [p.strip() for p in parts if p.strip()]


def _anchor_coverage(prompt: str, anchors: list) -> float:
    """Fraction of a character's canonical anchors that appear verbatim in the prompt."""
    if not anchors:
        return 1.0
    hits = sum(1 for a in anchors if a and a in prompt)
    return hits / len(anchors)


def _check_character_consistency(prompt: str, characters: list) -> list:
    """Warn when a named character's canonical anchors aren't restated in a scene.

    LTX-2.3 has no cross-clip memory, so a character's fixed look must be re-stated —
    using the SAME anchor words — in every fresh prompt they appear in, or their hair,
    build, and clothing drift shot to shot. If the character's name is in the prompt but
    fewer than half their canonical anchors are, flag it (the exact drift failure mode).
    """
    notes = []
    for c in characters:
        name = c.get("name", "")
        desc = c.get("description", "")
        if not name or not desc or name not in prompt:
            continue
        anchors = _appearance_anchors(desc)
        if _anchor_coverage(prompt, anchors) < 0.5:
            notes.append(
                f"character '{name}' is named but few of their canonical anchors "
                f"({desc}) are restated verbatim — restate the fixed look to stop it "
                f"drifting (a continuation clip carried from the previous frame in "
                f"DrawThings may keep this light)")
    return notes



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
    enable_utf8_stdout()
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
    chapter_path = os.path.join(args.project, chapter["file"])
    if not os.path.isfile(chapter_path):
        raise SystemExit(f"ERROR: chapter file missing: {chapter_path}")
    chapter_doc = load_json(chapter_path)  # carries source_text + chapter metadata

    scenes_in, characters_in = _load_payload(args.scenes)
    characters = _normalize_characters(characters_in)

    canonical = []
    warnings = []
    for i, s in enumerate(scenes_in, start=1):
        prompt = str(s.get("prompt", "")).strip()
        if not prompt:
            raise SystemExit(f"ERROR: scene {i} has an empty prompt.")
        excerpt = str(s.get("source_excerpt", "")).strip()
        if not excerpt:
            warnings.append(f"scene {i}: no source_excerpt (mapping back to novel will be weak)")
        neg = str(s.get("negative_prompt", "")).strip()
        try:
            dur = int(s.get("suggested_duration_seconds", 6) or 6)
        except (TypeError, ValueError):
            dur = 6
        continuation = bool(s.get("continuation", False))
        end_state = str(s.get("end_state", "")).strip()

        # Integrate any spoken lines into the single main prompt — LTX-2.3 has no
        # separate transcript input, so a line only gets voiced if it's in the prompt.
        dialogue = _normalize_dialogue(s.get("dialogue"))
        prompt, added = _embed_dialogue(prompt, dialogue)
        if added:
            warnings.append(
                f"scene {i}: auto-embedded {len(added)} dialogue line(s) into the prompt "
                f"(they weren't woven in). Review scene {i} in {chapter['file']} for phrasing.")

        # Default the negative to the prompt's own language (LTX-2 ships localized
        # Negatives are authored by the agent in the scene's own language; the script
        # never translates. Fall back to a generic English negative only for English
        # prompts. For a CJK prompt with no (or an English) negative, warn the agent to
        # write a localized one rather than shipping a mismatched/mistranslated string.
        if not neg:
            neg = default_negative(prompt)
            if not neg:  # CJK prompt, no English fallback applied
                warnings.append(f"scene {i}: no negative_prompt — author one in the "
                                f"prompt's language (the script does not translate)")
        elif is_cjk(prompt) and not is_cjk(neg):
            warnings.append(f"scene {i}: negative_prompt looks English but the prompt is "
                            f"CJK — author the negative in the prompt's language")

        wc = word_count(prompt)
        if wc > 200:
            warnings.append(f"scene {i}: prompt is {wc} words (>200); consider trimming")

        for note in _check_character_consistency(prompt, characters):
            warnings.append(f"scene {i}: {note}")

        speech_secs = sum(estimate_speech_seconds(d["line"]) for d in dialogue)
        if dialogue and speech_secs > dur:
            warnings.append(
                f"scene {i}: dialogue needs ~{speech_secs:.1f}s but clip is {dur}s; "
                f"shorten the line or raise suggested_duration_seconds")

        canonical.append({
            "index": i,
            "title": str(s.get("title", "")).strip() or f"Scene {i}",
            "source_excerpt": excerpt,
            "prompt": prompt,
            "negative_prompt": neg,
            "suggested_duration_seconds": dur,
            "continuation": continuation,
            "end_state": end_state,
            "dialogue": dialogue,
            "estimated_speech_seconds": round(speech_secs, 1),
            "prompt_word_count": wc,
        })

    # Continuity checks: a "continuation" scene is rendered image-to-video from the
    # previous clip's last frame (DrawThings carries it over natively), so it must have a
    # predecessor that defines an end_state describing that seam frame.
    for c in canonical:
        i = c["index"]
        if c["continuation"]:
            if i == 1:
                warnings.append("scene 1: continuation=true but there is no previous clip "
                                "to continue from; set it to false or reorder")
            else:
                prev = canonical[i - 2]
                if not prev["end_state"]:
                    warnings.append(f"scene {i}: continues from scene {i-1}, but scene {i-1} "
                                    f"has no end_state — add one so this prompt can match the seam")

    # Fill the chapter file in place, preserving source_text and chapter metadata.
    chapter_doc["characters"] = characters
    chapter_doc["scene_count"] = len(canonical)
    chapter_doc["status"] = "generated"
    chapter_doc["scenes"] = canonical
    dump_json(chapter_path, chapter_doc)

    cast_notes = _merge_project_cast(args.project, chapter["number"], characters)

    chapter["scene_count"] = len(canonical)
    chapter["status"] = "generated"
    dump_json(manifest_path, manifest)

    print(f"Saved {len(canonical)} scene(s) for chapter {chapter['number']} -> "
          f"{chapter_path}")
    if characters:
        print(f"  cast: {len(characters)} character(s) recorded -> characters.json")
    with_dialogue = sum(1 for c in canonical if c["dialogue"])
    print(f"  dialogue coverage: {with_dialogue}/{len(canonical)} scene(s) have a spoken line")
    silent = [c["index"] for c in canonical if not c["dialogue"]]
    if silent:
        print(f"  NOTE: no dialogue in scene(s) {silent} — add a spoken line unless truly impossible")
    chained = [c["index"] for c in canonical if c["continuation"]]
    if chained:
        print(f"  continuity: scene(s) {chained} continue from the previous clip's last frame.")
        print(f"  Render the chapter's scenes in order; in DrawThings, start each of these "
              f"scenes from the previous clip's last frame (image-to-video / 'use last "
              f"frame') so the seam is invisible.")
    for n in cast_notes:
        print(f"  NOTE: {n}")
    for w in warnings:
        print(f"  WARNING: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
