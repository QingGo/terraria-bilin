"""从 Terraria.exe 提取内嵌的本地化 JSON 资源。

输出结构:
    _export/{lang}/{资源名}.json   每个资源一个 JSON 文件
    _export/manifest.json          gameVersion / dllSha1 / exportedAt / 统计
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import dnfile

RESOURCE_PREFIX = "Terraria.Localization.Content."

# Terraria 内嵌 JSON 允许尾部逗号，标准 json 模块不允许，需清洗
_TRAILING_COMMA = re.compile(r",\s*([}\]])")

DEFAULT_EXE = r"D:\steam\steamapps\common\Terraria\Terraria.exe"
ALL_LANGUAGES = [
    "en-US", "de-DE", "it-IT", "fr-FR", "zh-Hans",
    "es-ES", "ru-RU", "pt-BR", "pl-PL", "ja-JP", "ko-KR", "zh-Hant",
]


def parse_json_lenient(data: bytes) -> dict:
    """解析允许尾部逗号的游戏内嵌 JSON。"""
    text = data.decode("utf-8")
    cleaned = _TRAILING_COMMA.sub(r"\1", text)
    return json.loads(cleaned)


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def extract(exe_path: Path, export_dir: Path, languages: list[str]) -> Path:
    pe = dnfile.dnPE(str(exe_path))
    resources = {str(r.name): r for r in pe.net.resources}

    stats: dict[str, dict[str, int]] = {}
    total_files = 0
    for lang in sorted(languages):
        out_dir = export_dir / lang
        out_dir.mkdir(parents=True, exist_ok=True)
        stats[lang] = {"files": 0, "keys": 0}
        for name, res in sorted(resources.items()):
            if not name.startswith(RESOURCE_PREFIX):
                continue
            rel = name[len(RESOURCE_PREFIX):]
            if not (rel == f"{lang}.json" or rel.startswith(f"{lang}.")):
                continue
            if res.data is None:
                raise RuntimeError(f"资源 {name} 无内嵌数据（可能是外部文件引用）")
            data = parse_json_lenient(res.data)
            (out_dir / rel).write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            stats[lang]["files"] += 1
            stats[lang]["keys"] += sum(len(v) for v in data.values())
            total_files += 1

    if stats[list(stats)[0]]["files"] == 0:
        raise RuntimeError(
            f"未在 {exe_path} 中找到任何 {languages[0]} 本地化资源，"
            "请确认游戏版本与资源命名"
        )

    version = getattr(exe_path, "version", None)
    manifest = {
        "gameVersion": _read_game_version(exe_path),
        "dllSha1": sha1_file(exe_path),
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "languages": stats,
        "sourceExe": str(exe_path),
    }
    manifest_path = export_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), "utf-8")
    return manifest_path


def _read_game_version(exe_path: Path) -> str:
    try:
        pe = dnfile.dnPE(str(exe_path))
        a = pe.net.mdtables.Assembly.rows[0]
        return ".".join(
            str(getattr(a, f)) for f in ("MajorVersion", "MinorVersion", "BuildNumber", "RevisionNumber")
        )
    except Exception:
        return "unknown"


def main() -> None:
    ap = argparse.ArgumentParser(description="从 Terraria.exe 提取本地化 JSON 资源")
    ap.add_argument("--exe", default=DEFAULT_EXE, help="Terraria.exe 路径")
    ap.add_argument("--export-dir", type=Path, default=Path("_export"))
    ap.add_argument("--languages", nargs="+", default=["en-US", "zh-Hans"])
    ap.add_argument("--all-languages", action="store_true", help="提取全部 12 种语言")
    args = ap.parse_args()

    exe = Path(args.exe)
    if not exe.is_file():
        raise SystemExit(f"找不到游戏可执行文件: {exe}")
    languages = ALL_LANGUAGES if args.all_languages else args.languages
    manifest = extract(exe, args.export_dir, languages)
    print(f"提取完成, manifest: {manifest}")
    for lang, s in json.loads(manifest.read_text("utf-8"))["languages"].items():
        print(f"  {lang}: {s['files']} 个文件, {s['keys']} 个 key")


if __name__ == "__main__":
    main()
