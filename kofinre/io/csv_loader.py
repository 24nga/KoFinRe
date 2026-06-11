"""CSV 입출력."""
import csv
import re
from pathlib import Path
from typing import List, Dict


def load_req_abstract(path: Path) -> List[Dict]:
    """REQ_abstract.csv 형식 로드.

    필드: project_id, project_name, system_name, req_id, req_title, req_details
    """
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    return rows


def split_sub_requirements(req_details: str) -> List[str]:
    """req_details 안 sub-requirement를 세미콜론 분리."""
    parts = re.split(r'[;；]', req_details or '')
    return [p.strip() for p in parts if p.strip()]


def save_csv(path: Path, rows: List[Dict], fieldnames: List[str] = None):
    """UTF-8 BOM 형식 (Excel 친화)."""
    if not rows:
        Path(path).write_text('', encoding='utf-8-sig')
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in fieldnames})
