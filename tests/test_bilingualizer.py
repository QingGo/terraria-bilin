import pytest

from bilingualizer import (
    bilingualize,
    format_dual,
    is_placeholder_compatible,
    placeholders,
)


class TestPlaceholders:
    def test_numeric(self):
        assert placeholders("{0} has defeated {1}") == {"0", "1"}

    def test_named_and_refs(self):
        assert placeholders("{$ItemName.X} {PlayerName}") == {"$ItemName.X", "PlayerName"}

    def test_conditional(self):
        assert placeholders("{?Day} {?!Night}") == {"?Day", "?!Night"}


class TestCompatibility:
    @pytest.mark.parametrize(
        "en,zh,ok",
        [
            ("{0} has defeated {1}", "{0} 击败了 {1}", True),
            ("{0} hit you for {1}", "{1} 伤害", False),
            ("{$ItemName.Sword}", "{$ItemName.Sword}", True),
            ("{PlayerName} joined", "{PlayerName} 加入了", True),
            ("{PlayerName} joined", "{0} 加入了", False),
        ],
    )
    def test_compat(self, en, zh, ok):
        assert is_placeholder_compatible(en, zh) is ok


class TestFormatDual:
    def test_short_single_line(self):
        assert format_dual("Copper Shortsword", "铜短剑") == "Copper Shortsword / 铜短剑"

    def test_long_two_lines(self):
        en = "x" * 50
        zh = "很长的中文" * 10
        assert format_dual(en, zh) == f"{en}\n{zh}"

    def test_embedded_newline_two_lines(self):
        assert format_dual("a\nb", "甲\n乙") == "a\nb\n甲\n乙"

    def test_threshold(self):
        en = "x" * 40
        zh = "中" * 30
        assert format_dual(en, zh) == f"{en} / {zh}"


class TestBilingualize:
    def test_basic_pair(self):
        en = {"ItemName": {"CopperShortsword": "Copper Shortsword"}}
        zh = {"ItemName": {"CopperShortsword": "铜短剑"}}
        r = bilingualize(en, zh)
        assert r.en_first["ItemName"]["CopperShortsword"] == "Copper Shortsword / 铜短剑"
        # 中文语言文件同样英文在前
        assert r.zh_first["ItemName"]["CopperShortsword"] == "Copper Shortsword / 铜短剑"
        assert r.dual_count == 1

    def test_identical_skipped(self):
        en = {"ItemName": {"Golf": "Golf"}}
        zh = {"ItemName": {"Golf": "Golf"}}
        r = bilingualize(en, zh)
        assert r.dual_count == 0
        assert r.skipped[0].skipped_reason == "双语相同"

    def test_missing_zh_skipped(self):
        en = {"ItemName": {"X": "X Sword"}}
        zh = {"ItemName": {}}
        r = bilingualize(en, zh)
        assert r.dual_count == 0
        assert r.skipped[0].skipped_reason == "zh 缺失"

    def test_placeholder_mismatch_skipped(self):
        en = {"UI": {"K": "{0} and {1}"}}
        zh = {"UI": {"K": "{1}"}}
        r = bilingualize(en, zh)
        assert r.dual_count == 0
        assert "占位符不一致" in r.skipped[0].skipped_reason

    def test_short_ui_label_single(self):
        en = {"UI": {"TimeAtMorning": "AM"}}
        zh = {"UI": {"TimeAtMorning": "上午"}}
        r = bilingualize(en, zh)
        assert r.dual_count == 0
        assert r.single_count == 1

    def test_ui_word_now_dual(self):
        en = {"UI": {"PlayerCreateCategoryEyeColor": "Eyes"}}
        zh = {"UI": {"PlayerCreateCategoryEyeColor": "眼睛"}}
        r = bilingualize(en, zh)
        assert r.dual_count == 1

    def test_long_ui_phrase_dual(self):
        en = {"UI": {"QuickUseItem": "Quick Use"}}
        zh = {"UI": {"QuickUseItem": "快速使用"}}
        r = bilingualize(en, zh)
        assert r.dual_count == 1

    def test_excluded_category(self):
        en = {"Key": {"UP": "UP"}}
        zh = {"Key": {"UP": "上"}}
        r = bilingualize(en, zh)
        assert r.excluded_count == 1
        assert r.dual_count == 0

    def test_random_world_name_single(self):
        en = {"RandomWorldName_Adjective": {"1": "Lonely"}}
        zh = {"RandomWorldName_Adjective": {"1": "孤独"}}
        r = bilingualize(en, zh)
        assert r.single_count == 1
        assert r.dual_count == 0
