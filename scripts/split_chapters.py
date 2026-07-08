"""Split a novel .txt into chapters and scaffold the output project.

This is the deterministic first step of the skill. It does NOT write any prompts —
it just parses chapters and lays out one scenes.json per chapter (carrying the verbatim
chapter text) so the agent can read each chapter and decide scene boundaries.

Usage:
    python split_chapters.py NOVEL.txt --out OUTPUT_DIR [--title NAME] [--regex RE]

Produces:
    OUTPUT_DIR/<novel-slug>/
        manifest.json                       # index of chapters + status tracking
        chapter-001-<slug>.json             # {chapter_number, chapter_title, word_count,
                                            #  source_text, status, characters, scenes:[]}
        chapter-002-<slug>.json ...

The agent reads each chapter file's `source_text`, plans scenes, and hands them to
save_scenes.py, which fills the same chapter file in place. Each chapter is a single flat
JSON file — there are no per-chapter folders, source.txt, or chapter.json.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (  # noqa: E402
    DEFAULT_CHAPTER_REGEX,
    RECOMMENDED_PARAMS,
    chapter_filename,
    dump_json,
    enable_utf8_stdout,
    parse_chapters,
    read_text,
    slugify,
    word_count,
)


def main() -> int:
    enable_utf8_stdout()
    ap = argparse.ArgumentParser(description="Split a novel into chapters and scaffold output.")
    ap.add_argument("novel", help="Path to the novel .txt file")
    ap.add_argument("--out", required=True, help="Output root directory")
    ap.add_argument("--title", help="Novel title (defaults to the file name)")
    ap.add_argument("--regex", default=DEFAULT_CHAPTER_REGEX,
                    help="Chapter marker regex (multiline, case-insensitive)")
    args = ap.parse_args()

    novel_path = os.path.abspath(args.novel)
    if not os.path.isfile(novel_path):
        print(f"ERROR: novel file not found: {novel_path}", file=sys.stderr)
        return 2

    title = args.title or os.path.splitext(os.path.basename(novel_path))[0]
    text = read_text(novel_path)
    chapters = parse_chapters(text, args.regex)
    if not chapters:
        print("ERROR: no text content found in the novel file.", file=sys.stderr)
        return 2

    project_dir = os.path.join(os.path.abspath(args.out), slugify(title, max_len=60))
    os.makedirs(project_dir, exist_ok=True)

    manifest_chapters = []
    for ch in chapters:
        fname = chapter_filename(ch["number"], ch["title"])

        # One self-contained flat file per chapter: the verbatim text lives here as
        # source_text, and save_scenes.py fills in characters + scenes in place.
        dump_json(os.path.join(project_dir, fname), {
            "chapter_number": ch["number"],
            "chapter_title": ch["title"],
            "word_count": word_count(ch["text"]),
            "source_text": ch["text"],
            "status": "pending",  # pending -> generated (after save_scenes.py)
            "characters": [],
            "scene_count": 0,
            "scenes": [],
        })
        manifest_chapters.append({
            "number": ch["number"],
            "title": ch["title"],
            "file": fname,
            "word_count": word_count(ch["text"]),
            "scene_count": None,
            "status": "pending",  # pending -> generated (after save_scenes.py)
        })

    dump_json(os.path.join(project_dir, "manifest.json"), {
        "novel": title,
        "source_file": novel_path,
        "created": _dt.datetime.now().isoformat(timespec="seconds"),
        "recommended_params": RECOMMENDED_PARAMS,
        "chapter_count": len(chapters),
        "chapters": manifest_chapters,
    })

    print(f"Project created: {project_dir}")
    print(f"Parsed {len(chapters)} chapter(s). Read each chapter file's source_text, "
          f"then call save_scenes.py.\n")
    for c in manifest_chapters:
        cf = os.path.join(project_dir, c["file"])
        print(f"  Ch {c['number']:>3}  {c['word_count']:>6} words  {cf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


