"""双语化核心引擎：en/zh 配对、占位符检查、格式决策。"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from policy import classify

_PLACEHOLDER = re.compile(r"{([^{}]*)}")

DUAL_LINE_SEP = " / "
DUAL_LINE_MAX = 40  # 任一侧超过该字符数 → 双行 EN\\n中文


def load_language(export_dir: Path, lang: str) -> dict[str, dict[str, str]]:
    """合并 _export/{lang}/*.json 为 {Category: {Key: text}}。"""
    merged: dict[str, dict[str, str]] = {}
    lang_dir = export_dir / lang
    if not lang_dir.is_dir():
        raise FileNotFoundError(f"缺少导出数据目录: {lang_dir}")
    for path in sorted(lang_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for category, keys in data.items():
            merged.setdefault(category, {}).update(keys)
    return merged


def placeholders(text: str) -> frozenset[str]:
    """提取文本中的占位符 token 集合（{$ref}、{?cond}、{0}、{Name}）。"""
    return frozenset(_PLACEHOLDER.findall(text))


def is_placeholder_compatible(en: str, zh: str) -> bool:
    """en/zh 占位符集合必须一致，否则 string.Format 双填可能异常。"""
    return placeholders(en) == placeholders(zh)


def format_dual(en: str, zh: str) -> str:
    """格式决策：短文本单行 'EN / 中文'，长文本/多行双行 'EN\\n中文'。"""
    if "\n" in en or "\n" in zh:
        return f"{en}\n{zh}"
    if max(len(en), len(zh)) > DUAL_LINE_MAX:
        return f"{en}\n{zh}"
    return f"{en}{DUAL_LINE_SEP}{zh}"


@dataclass
class Decision:
    category: str
    key: str
    en: str
    zh: str | None
    policy: str
    skipped_reason: str = ""
    dual_text: str = ""


@dataclass
class BilingualResult:
    """两个语言文件输出（均为 EN / 中文 顺序）+ 统计。"""
    en_first: dict[str, dict[str, str]] = field(default_factory=dict)
    zh_first: dict[str, dict[str, str]] = field(default_factory=dict)
    dual_count: int = 0
    single_count: int = 0
    excluded_count: int = 0
    skipped: list[Decision] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"DUAL {self.dual_count} 条, SINGLE {self.single_count} 条, "
            f"EXCLUDE {self.excluded_count} 条"
        )


def bilingualize(en_data: dict, zh_data: dict) -> BilingualResult:
    """对 en/zh 两套数据执行配对与双语化。"""
    result = BilingualResult()
    for category in sorted(en_data):
        en_keys = en_data[category]
        zh_keys = zh_data.get(category, {})
        for key in sorted(en_keys):
            en = en_keys[key]
            decision = _decide(category, key, en, zh_keys.get(key))
            if decision.policy != "DUAL" or decision.dual_text == "":
                result.skipped.append(decision)
                if decision.policy == "SINGLE":
                    result.single_count += 1
                elif decision.policy == "EXCLUDE":
                    result.excluded_count += 1
                continue
            result.en_first.setdefault(category, {})[key] = decision.dual_text
            result.zh_first.setdefault(category, {})[key] = decision.dual_text
            result.dual_count += 1
    return result


def _decide(category: str, key: str, en: str, zh: str | None) -> Decision:
    policy = classify(category, en)
    d = Decision(category=category, key=key, en=en, zh=zh, policy=policy)
    if policy != "DUAL":
        return d
    if zh is None:
        d.skipped_reason = "zh 缺失"
        return d
    if en == zh:
        d.skipped_reason = "双语相同"
        return d
    if not en or not zh:
        d.skipped_reason = "空文本"
        return d
    if not is_placeholder_compatible(en, zh):
        d.skipped_reason = f"占位符不一致 {sorted(placeholders(en))} != {sorted(placeholders(zh))}"
        return d
    d.dual_text = format_dual(en, zh)
    return d
