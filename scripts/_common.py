"""Shared helpers for the NovelVideoPromptMaker skill scripts.

Kept dependency-free (standard library only) so the skill runs anywhere Python 3.8+
is available, with no install step.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

# Chapter marker: matches "Chapter 1", "Chapter XII: Title", "CHAPTER 3 - Dawn",
# and common CJK forms — Chinese "第1章"/"第十二章 标题" and Japanese "第一話"/"第3回".
# Covers unit chars 章 (chapter), 回/話/话 (episode), 節/节 (section) and kanji digits.
DEFAULT_CHAPTER_REGEX = (
    r"^\s*(?:chapter\s+[\divxlcdm]+\b"
    r"|第\s*[\d〇零一二三四五六七八九十百千两]+\s*[章回話话節节])\s*.*$"
)

RECOMMENDED_PARAMS = {
    "sampling_steps": 24,
    "cfg_scale": 6.5,
    "fps": 25,
    "resolution": "720p",
}

MAX_PROMPT_WORDS = 200


def slugify(text: str, max_len: int = 40) -> str:
    """Filesystem-friendly slug; keeps unicode word chars so CJK titles survive."""
    text = (text or "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")
    return text or "untitled"


def read_text(path: str | Path) -> str:
    """Read a text file tolerating BOM and common encodings (UTF-8, GB18030)."""
    raw = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_json(path: str | Path) -> dict:
    return json.loads(read_text(path))


def dump_json(path: str | Path, data) -> None:
    Path(path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def word_count(text: str) -> int:
    """Approximate word count that also works for CJK text.

    Whitespace tokenization undercounts Chinese/Japanese/Korean (no spaces between
    words), so count each CJK ideograph/kana as one unit plus whitespace tokens from
    the remaining (Latin, etc.) text. Keeps the LTX-2.3 200-word prompt check honest
    for mixed-language prompts.
    """
    text = text or ""
    cjk = re.findall(
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7a3]", text
    )
    non_cjk = re.sub(
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7a3]", " ", text
    )
    return len(cjk) + len(re.findall(r"\S+", non_cjk))


# Rough speaking rates for fitting dialogue into a clip. LTX-2.3 renders short clips,
# so a line that takes longer than the clip to say will be cut off or desynced.
_LATIN_WORDS_PER_SEC = 2.5   # ~150 wpm, natural narrative delivery
_CJK_CHARS_PER_SEC = 5.0     # ~5 kana/hanzi per second


def estimate_speech_seconds(text: str) -> float:
    """Estimate how long a spoken line takes to say, CJK- and Latin-aware.

    Used to warn when a scene's dialogue is too long to fit its clip duration —
    a common cause of cut-off or desynced speech in LTX-2.3.
    """
    text = text or ""
    cjk = re.findall(
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7a3]", text
    )
    non_cjk = re.sub(
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7a3]", " ", text
    )
    latin_words = len(re.findall(r"\S+", non_cjk))
    return len(cjk) / _CJK_CHARS_PER_SEC + latin_words / _LATIN_WORDS_PER_SEC


def parse_chapters(text: str, chapter_regex: str = DEFAULT_CHAPTER_REGEX) -> List[dict]:
    """Split novel text into [{number, title, text}].

    Text before the first marker is dropped. If no markers are found, the whole
    document becomes a single chapter so the skill still works on marker-less files.
    """
    pattern = re.compile(chapter_regex, re.IGNORECASE | re.MULTILINE)
    matches = list(pattern.finditer(text))

    if not matches:
        body = text.strip()
        return [{"number": 1, "title": "Chapter 1", "text": body}] if body else []

    chapters: List[dict] = []
    for i, match in enumerate(matches):
        title = match.group(0).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if not body:
            continue
        chapters.append({"number": len(chapters) + 1, "title": title, "text": body})
    return chapters


def chapter_dirname(number: int, title: str) -> str:
    return f"chapter-{number:03d}-{slugify(title)}"
