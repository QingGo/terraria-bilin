"""生成官方 Language Pack 资源包（pack.json + Content/Localization/*.json + zip）。"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bilingualizer import bilingualize, load_language

PACK_NAME = "terraria-bilingual-pack"
PACK_AUTHOR = "QingGo"
PACK_VERSION = (0, 1, 0)
EN_LANG = "en-US"
ZH_LANG = "zh-Hans"


def write_pack(export_dir: Path, output_dir: Path) -> Path:
    pack_dir = output_dir / PACK_NAME
    content_dir = pack_dir / "Content" / "Localization"
    content_dir.mkdir(parents=True, exist_ok=True)

    en_data = load_language(export_dir, EN_LANG)
    zh_data = load_language(export_dir, ZH_LANG)
    result = bilingualize(en_data, zh_data)

    for lang, lang_data in ((EN_LANG, result.en_first), (ZH_LANG, result.zh_first)):
        lang_path = content_dir / f"{lang}-Bilingual.json"
        lang_path.write_text(
            json.dumps(lang_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    pack_json = {
        "Name": "Terraria Bilingual Pack (EN / 中文)",
        "Author": PACK_AUTHOR,
        "Description": "Bilingual display pack: shows English and Simplified Chinese side by side. 英中双语显示资源包。",
        "Version": {
            "major": PACK_VERSION[0],
            "minor": PACK_VERSION[1],
        },
    }
    (pack_dir / "pack.json").write_text(
        json.dumps(pack_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 官方要求：zip 内 pack.json 必须在根目录（直接压缩包内容，不包外层文件夹）
    zip_path = output_dir / f"{PACK_NAME}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pack_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(pack_dir))
    return zip_path


def main() -> None:
    ap = argparse.ArgumentParser(description="构建双语资源包并打包 zip")
    ap.add_argument("--export-dir", type=Path, default=Path("_export"))
    ap.add_argument("--output-dir", type=Path, default=Path("output"))
    args = ap.parse_args()

    zip_path = write_pack(args.export_dir, args.output_dir)
    print(f"资源包已生成: {zip_path}")
    print(f"大小: {zip_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
