"""全量验证：资源包 JSON 合法性、key 配对、占位符平衡、manifest 新鲜度。"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bilingualizer import load_language, placeholders

EN_LANG = "en-US"
ZH_LANG = "zh-Hans"


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_manifest(export_dir: Path, exe: Path | None) -> list[str]:
    warnings = []
    manifest_path = export_dir / "manifest.json"
    if not manifest_path.exists():
        return ["缺少 manifest.json，无法校验数据新鲜度"]
    manifest = json.loads(manifest_path.read_text("utf-8"))
    if exe and exe.is_file() and sha1_file(exe) != manifest.get("dllSha1"):
        warnings.append(
            "Terraria.exe 已被修改，导出数据可能过期，请重新运行 extract_exe.py"
        )
    if manifest.get("gameVersion") not in (None, "unknown"):
        pass
    return warnings


def verify(export_dir: Path, pack_dir: Path, exe: Path | None) -> list[str]:
    errors: list[str] = []
    warnings = check_manifest(export_dir, exe)

    en_data = load_language(export_dir, EN_LANG)
    zh_data = load_language(export_dir, ZH_LANG)

    for lang, source in ((EN_LANG, en_data), (ZH_LANG, zh_data)):
        pack_file = pack_dir / "Content" / "Localization" / f"{lang}-Bilingual.json"
        if not pack_file.exists():
            errors.append(f"缺少语言文件: {pack_file}")
            continue
        pack = json.loads(pack_file.read_text("utf-8"))
        if not isinstance(pack, dict) or not all(
            isinstance(v, dict) for v in pack.values()
        ):
            errors.append(f"{pack_file}: 结构应为 {{Category: {{Key: text}}}}")
            continue
        for category, keys in pack.items():
            if category not in source:
                errors.append(f"{lang}: 包中分类 {category} 不存在于源数据")
                continue
            for key, text in keys.items():
                if key not in source[category]:
                    errors.append(f"{lang}: 包中 key {category}.{key} 不存在于源数据")
                    continue
                original = source[category][key]
                if text == original:
                    errors.append(f"{lang}: {category}.{key} 与原文相同（未双语化）")
                if "{" in text and "}" in text:
                    other_lang = zh_data if lang == EN_LANG else en_data
                    if category in other_lang and key in other_lang[category]:
                        if placeholders(text) != placeholders(
                            f"{original}{other_lang[category][key]}"
                        ):
                            errors.append(
                                f"{lang}: {category}.{key} 占位符集合与源数据不一致: {text!r}"
                            )

    total_keys = sum(
        len(keys) for data in (en_data, zh_data) for keys in data.values()
    )
    dual_count = sum(
        len(keys)
        for data in (pack_dir / "Content" / "Localization").glob("*-Bilingual.json")
        for keys in json.loads(data.read_text("utf-8")).values()
    ) // 2
    print(f"源数据 key 总数(双语言): {total_keys}")
    print(f"双语替换 key 数: {dual_count}")
    return errors + warnings


def main() -> None:
    ap = argparse.ArgumentParser(description="验证资源包数据一致性")
    ap.add_argument("--export-dir", type=Path, default=Path("_export"))
    ap.add_argument("--pack-dir", type=Path, default=Path("output/terraria-bilingual-pack"))
    ap.add_argument("--exe", type=Path, default=None)
    args = ap.parse_args()

    problems = verify(args.export_dir, args.pack_dir, args.exe)
    if problems:
        print("\n发现问题:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print("验证通过")


if __name__ == "__main__":
    main()
