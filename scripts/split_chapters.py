"""Split a novel .txt into chapters and scaffold the output project.

This is the deterministic first step of the skill. It does NOT write any prompts —
it just parses chapters and lays out folders so the agent can read each chapter's
source and decide scene boundaries.

Usage:
    python split_chapters.py NOVEL.txt --out OUTPUT_DIR [--title NAME] [--regex RE]

Produces:
    OUTPUT_DIR/<novel-slug>/
        manifest.json                 # index of chapters + status tracking
        chapter-001-<slug>/
            source.txt                # verbatim chapter text (read this to write scenes)
            chapter.json              # {number, title, char_count, word_count}
        chapter-002-<slug>/ ...
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
    chapter_dirname,
    dump_json,
    parse_chapters,
    read_text,
    slugify,
    word_count,
)


def main() -> int:
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
        dirname = chapter_dirname(ch["number"], ch["title"])
        ch_dir = os.path.join(project_dir, dirname)
        os.makedirs(ch_dir, exist_ok=True)

        with open(os.path.join(ch_dir, "source.txt"), "w", encoding="utf-8") as fh:
            fh.write(ch["text"])
        dump_json(os.path.join(ch_dir, "chapter.json"), {
            "number": ch["number"],
            "title": ch["title"],
            "char_count": len(ch["text"]),
            "word_count": word_count(ch["text"]),
        })
        manifest_chapters.append({
            "number": ch["number"],
            "title": ch["title"],
            "dir": dirname,
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
    print(f"Parsed {len(chapters)} chapter(s). Read each source.txt, then call save_scenes.py.\n")
    for c in manifest_chapters:
        src = os.path.join(project_dir, c["dir"], "source.txt")
        print(f"  Ch {c['number']:>3}  {c['word_count']:>6} words  {src}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
