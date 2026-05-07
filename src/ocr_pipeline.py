"""
Cleaned OCR pipeline skeleton for Thai Election OCR Challenge.

This file is designed for portfolio readability.
The full experimental workflow is available in the notebook.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from postprocess_votes import choose_vote_value


def get_document_pages(images_dir: str | Path, doc_id: str) -> list[Path]:
    """
    Return all PNG pages for a document ID.

    Example:
    party_list_34_11.png
    party_list_34_11_page2.png
    party_list_34_11_page3.png
    """
    images_dir = Path(images_dir)
    pages: list[Path] = []

    first_page = images_dir / f"{doc_id}.png"
    if first_page.exists():
        pages.append(first_page)

    page_no = 2
    while True:
        page_path = images_dir / f"{doc_id}_page{page_no}.png"
        if not page_path.exists():
            break
        pages.append(page_path)
        page_no += 1

    return pages


def build_ocr_prompt(expected_rows: int, doc_type: str) -> str:
    """Build a strict JSON-only prompt for Vision LLM OCR."""
    if doc_type == "party_list":
        order_text = f"เรียงตามหมายเลขพรรคจากบนลงล่าง ต้องมี {expected_rows} แถว"
    else:
        order_text = f"เรียงจากบนลงล่างตามลำดับแถวในตาราง ต้องมี {expected_rows} แถว"

    return f"""
คุณคือผู้เชี่ยวชาญ OCR เอกสารเลือกตั้งภาษาไทย

งานของคุณ:
1) อ่านเฉพาะคอลัมน์ "ได้คะแนน"
2) สำหรับแต่ละแถว ให้ดึง:
   - d = ตัวเลขที่เห็น
   - w = คำอ่านในวงเล็บ
3) ไม่รวม header
4) ไม่รวมแถว "รวมคะแนนทั้งสิ้น" ใน rows
5) ต้องดึง bottom_total แยกต่างหาก
6) {order_text}

กฎการอ่าน:
- ถ้า d กับ w ไม่ตรงกัน ให้ระบุทั้งคู่
- ถ้าไม่มี w ให้ใส่ w=""
- ถ้าอ่านไม่ได้จริง ๆ ให้ d="" และ w=""
- อย่าข้ามแถว อย่าเพิ่มแถว

ส่ง JSON เท่านั้น:
{{
  "rows": [
    {{"d": "๓๔,๑๗๗", "w": "สามหมื่นสี่พันหนึ่งร้อยเจ็ดสิบเจ็ด"}}
  ],
  "bottom_total": {{"d": "๗๗,๐๗๕", "w": "เจ็ดหมื่นเจ็ดพันเจ็ดสิบห้า"}},
  "notes": []
}}
""".strip()


def parse_ocr_payload(payload: dict[str, Any], expected_rows: int) -> dict[str, Any]:
    """
    Parse Vision LLM JSON output into normalized vote values.
    """
    rows = payload.get("rows", [])
    votes: list[int] = []
    sources: list[str] = []

    for row in rows:
        digit_text = str(row.get("d", "") or "")
        word_text = str(row.get("w", "") or "")
        value, source = choose_vote_value(digit_text, word_text)
        votes.append(value)
        sources.append(source)

    bottom_total = payload.get("bottom_total", {}) or {}
    total_value, total_source = choose_vote_value(
        bottom_total.get("d", ""),
        bottom_total.get("w", ""),
    )

    return {
        "votes": votes,
        "sources": sources,
        "meta": {
            "expected_rows": expected_rows,
            "n_rows": len(votes),
            "sum_votes": sum(votes),
            "bottom_total": total_value,
            "bottom_total_source": total_source,
            "ok_length": len(votes) == expected_rows,
            "ok_total": total_value > 0 and sum(votes) == total_value,
        },
    }


def build_submission(template_path: str | Path, predictions: dict[str, list[int]], output_path: str | Path) -> None:
    """
    Build final id,votes submission from a template and document-level predictions.

    `predictions` should map doc_id -> list of extracted vote counts in row order.
    """
    template = pd.read_csv(template_path)
    template["doc_id"] = template["id"].astype(str).apply(lambda x: x.rsplit("_", 1)[0])
    template["row_num"] = template["id"].astype(str).apply(lambda x: int(x.rsplit("_", 1)[1]))

    vote_map: dict[str, int] = {}

    for doc_id, group in template.groupby("doc_id"):
        group = group.sort_values("row_num")
        votes = predictions.get(doc_id, [0] * len(group))

        for i, (_, row) in enumerate(group.iterrows()):
            vote_map[str(row["id"])] = int(votes[i]) if i < len(votes) else 0

    template["votes"] = template["id"].astype(str).map(vote_map).fillna(0).astype(int)
    output = template[["id", "votes"]]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)


if __name__ == "__main__":
    print("This is a cleaned pipeline skeleton. Run the notebook for the full competition workflow.")
