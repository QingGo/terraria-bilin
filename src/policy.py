"""KeyPolicy v1：哪些 key 做双语、哪些保留单语。

策略（生成时应用，非运行时）：
- EXCLUDE    完全跳过（自引用文本 / 内部命令，双语无意义且有风险）
- SINGLE     保留原语言（空间敏感 / 生成随机名等）
- DUAL       替换为 "EN / 中文" 或 "EN\\n中文"

UI / GameUI 采用逐 key 规则：极短符号（<=3 字符）空间敏感 → SINGLE，其余短语 → DUAL。
"""
from __future__ import annotations

EXCLUDE_CATEGORIES = frozenset({
    "Key",           # 键盘键名 "UP"/"DOWN"，自引用
    "Language",      # 语言选择器名称，自引用
    "CLI",           # 服务器控制台命令
    "EmojiCommand",  # 聊天表情命令 "/{$EmojiName.X}"
    "Controls",      # 鼠标/键位名 "Left Click"
    "AssetRejections",  # 资源错误调试信息
})

SINGLE_PREFIXES = (
    "RandomWorldName_",  # 随机世界名词表，双语会生成奇怪的世界名
    "CreditsRollCategory_",  # 制作人员名单
)

UI_LIKE_CATEGORIES = frozenset({"UI", "GameUI"})

SHORT_LABEL_MAX = 3  # 字符数阈值：仅 AM/PM/HP 等极短符号保留单语


def classify(category: str, text_en: str) -> str:
    if category in EXCLUDE_CATEGORIES:
        return "EXCLUDE"
    if category.startswith(SINGLE_PREFIXES):
        return "SINGLE"
    if category in UI_LIKE_CATEGORIES:
        if len(text_en) <= SHORT_LABEL_MAX and " " not in text_en:
            return "SINGLE"
        return "DUAL"
    return "DUAL"
