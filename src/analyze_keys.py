"""key 类别统计 → KeyPolicy 数据支撑报告。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bilingualizer import load_language
from policy import classify


def analyze(export_dir: Path, lang: str) -> None:
    data = load_language(export_dir, lang)
    rows = []
    for category in sorted(data):
        keys = data[category]
        pol = {"DUAL": 0, "SINGLE": 0, "EXCLUDE": 0}
        for text in keys.values():
            pol[classify(category, text)] += 1
        rows.append((category, len(keys), pol["DUAL"], pol["SINGLE"], pol["EXCLUDE"]))
    print(f"{'Category':40s} {'total':>6s} {'DUAL':>6s} {'SINGLE':>7s} {'EXCL':>5s}")
    for category, total, dual, single, excl in sorted(rows, key=lambda r: -r[1]):
        print(f"{category:40s} {total:6d} {dual:6d} {single:7d} {excl:5d}")
    print(
        f"\n合计 {len(rows)} 类 / {sum(r[1] for r in rows)} key "
        f"/ DUAL {sum(r[2] for r in rows)} / SINGLE {sum(r[3] for r in rows)} "
        f"/ EXCLUDE {sum(r[4] for r in rows)}"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="输出各分类 key 的 KeyPolicy 统计")
    ap.add_argument("--export-dir", type=Path, default=Path("_export"))
    ap.add_argument("--lang", default="en-US")
    args = ap.parse_args()
    analyze(args.export_dir, args.lang)


if __name__ == "__main__":
    main()
