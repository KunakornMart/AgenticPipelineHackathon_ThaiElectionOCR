"""
Post-processing utilities for Thai Election OCR.

This module focuses on:
- Thai digit normalization
- Thai number-word parsing
- Vote string cleaning
- Basic vote validation
"""

from __future__ import annotations

import re
from typing import Optional, Tuple


THAI_DIGIT_MAP = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")

ONES = {
    "ศูนย์": 0,
    "หนึ่ง": 1,
    "เอ็ด": 1,
    "สอง": 2,
    "ยี่": 2,
    "สาม": 3,
    "สี่": 4,
    "ห้า": 5,
    "หก": 6,
    "เจ็ด": 7,
    "แปด": 8,
    "เก้า": 9,
}

MULTIPLIERS = [
    ("ล้าน", 1_000_000),
    ("แสน", 100_000),
    ("หมื่น", 10_000),
    ("พัน", 1_000),
    ("ร้อย", 100),
    ("สิบ", 10),
]


def normalize_thai_digits(text: str | None) -> str:
    """Convert Thai digits to Arabic digits."""
    if text is None:
        return ""
    return str(text).translate(THAI_DIGIT_MAP)


def clean_vote_digits(text: str | None) -> str:
    """Return only Arabic digits from a noisy OCR vote string."""
    if text is None:
        return ""
    text = normalize_thai_digits(str(text))
    text = text.replace(",", "")
    digits = re.findall(r"\d+", text)
    return "".join(digits)


def parse_thai_number_words(text: str | None) -> Optional[int]:
    """
    Parse common Thai number words into an integer.

    This parser is designed for vote-count text such as:
    - หนึ่งหมื่นสี่พันแปดร้อยสิบสาม
    - เจ็ดหมื่นเจ็ดพันเจ็ดสิบห้า
    """
    if not text:
        return None

    text = str(text)
    text = re.sub(r"[\s,()]+", "", text)

    if not text:
        return None

    total = 0
    remaining = text

    # Handle million blocks recursively in a simple way.
    if "ล้าน" in remaining:
        left, right = remaining.split("ล้าน", 1)
        left_value = parse_thai_number_words(left) or 1
        total += left_value * 1_000_000
        remaining = right

    for word, multiplier in MULTIPLIERS[1:]:
        if word in remaining:
            left, remaining = remaining.split(word, 1)
            if left == "":
                value = 1
            elif left == "ยี่" and word == "สิบ":
                value = 2
            else:
                value = ONES.get(left, parse_thai_number_words(left) or 0)
            total += value * multiplier

    if remaining:
        total += ONES.get(remaining, 0)

    return total if total > 0 else None


def choose_vote_value(digit_text: str | None, word_text: str | None) -> Tuple[int, str]:
    """
    Choose the most reliable vote value from digit and Thai-word OCR outputs.

    Rule:
    - If Thai words can be parsed, prefer them.
    - Otherwise use visible digits.
    - Return 0 if both are unavailable.
    """
    digit_clean = clean_vote_digits(digit_text)
    digit_value = int(digit_clean) if digit_clean else None

    word_value = parse_thai_number_words(word_text)

    if word_value is not None:
        return int(word_value), "thai_words"

    if digit_value is not None:
        return int(digit_value), "digits"

    return 0, "empty"


def is_valid_vote_string(value: str | int | None) -> bool:
    """Check whether a vote value is represented only by Arabic digits."""
    if value is None:
        return False
    return bool(re.fullmatch(r"\d+", str(value)))


if __name__ == "__main__":
    examples = [
        ("๑๔,๘๑๓", "หนึ่งหมื่นสี่พันแปดร้อยสิบสาม"),
        ("๗๗,๐๗๕", "เจ็ดหมื่นเจ็ดพันเจ็ดสิบห้า"),
        ("300", "สามร้อย"),
    ]

    for d, w in examples:
        value, source = choose_vote_value(d, w)
        print(f"{d!r}, {w!r} -> {value} ({source})")
