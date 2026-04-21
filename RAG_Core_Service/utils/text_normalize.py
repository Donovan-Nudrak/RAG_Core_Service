#!/usr/bin/env python3

import re

_NOISE_SCRIPTS = re.compile(
    "["
    "\u0590-\u05FF"  # Hebrew
    "\u0600-\u06FF"  # Arabic
    "\u0750-\u077F"  # Arabic supplement
    "\u08A0-\u08FF"  # Arabic extended-A
    "\uFB50-\uFDFF"  # Arabic presentacion forms-A
    "\uFE70-\uFEFF"  # Arabic presentacion forms-B
    "\u0400-\u04FF"  # Cyrillic
    "\u3040-\u30FF"  # Hiragana/Katakana
    "\u4E00-\u9FFF"  # CKJ Unfield ideographs
    "\uAC00-\uD7AF"  # Hangul
    "\u0E00-\u0E7F"  # Thai
    "\u0900-\u097F"  # Devanagari
    "]",
    re.UNICODE,
)

_ZW_AND_BOM = re.compile("[\u200B-\u200D\uFEFF]")


def normalize_answer_text(text: str) -> str:

    if not text:
        return text

    def _chr16(m: re.Match[str]) -> str:
        return chr(int(m.group(1), 16))

    def _chr32(m: re.Match[str]) -> str:
        return chr(int(m.group(1), 16))

    out = re.sub(r"\\u([0-9a-fA-F]{4})", _chr16, text)
    out = re.sub(r"\\U([0-9a-fA-F]{8})", _chr32, out)
    out = out.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")

    out = _ZW_AND_BOM.sub("", out)
    out = _NOISE_SCRIPTS.sub("", out)

    out = re.sub(r"\n{3,}", "\n\n", out)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r" *\n *", "\n", out)

    lines = [ln.strip() for ln in out.split("\n")]
    out = "\n".join(ln for ln in lines if ln)

    return out.strip()
