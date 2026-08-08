import json
import zipfile

from build_pack import EN_LANG, PACK_NAME, ZH_LANG, write_pack


def _write_fixture(export_dir, lang, data):
    d = export_dir / lang
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{lang}.json").write_text(json.dumps(data, ensure_ascii=False), "utf-8")


def test_build_pack_structure(tmp_path):
    export = tmp_path / "export"
    _write_fixture(
        export, EN_LANG, {"ItemName": {"CopperShortsword": "Copper Shortsword"}, "UI": {"Play": "Play"}}
    )
    _write_fixture(
        export, ZH_LANG, {"ItemName": {"CopperShortsword": "铜短剑"}, "UI": {"Play": "播放"}}
    )
    out = tmp_path / "out"
    zip_path = write_pack(export, out)

    assert zip_path.exists()
    pack_dir = out / PACK_NAME
    assert (pack_dir / "pack.json").is_file()
    pack_json = json.loads((pack_dir / "pack.json").read_text("utf-8"))
    assert pack_json["Name"]
    assert pack_json["Version"] == {"Major": 1, "Minor": 0, "Build": 0}

    en_path = pack_dir / "Content" / "Localization" / f"{EN_LANG}-Bilingual.json"
    zh_path = pack_dir / "Content" / "Localization" / f"{ZH_LANG}-Bilingual.json"
    assert en_path.is_file() and zh_path.is_file()

    en_pack = json.loads(en_path.read_text("utf-8"))
    zh_pack = json.loads(zh_path.read_text("utf-8"))
    assert en_pack["ItemName"]["CopperShortsword"] == "Copper Shortsword / 铜短剑"
    assert zh_pack["ItemName"]["CopperShortsword"] == "铜短剑 / Copper Shortsword"
    # 短 UI 标签不进入包
    assert "UI" not in en_pack and "UI" not in zh_pack

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        assert f"{PACK_NAME}/pack.json" in names
        assert f"{PACK_NAME}/Content/Localization/{EN_LANG}-Bilingual.json" in names
        assert f"{PACK_NAME}/Content/Localization/{ZH_LANG}-Bilingual.json" in names


def test_build_pack_missing_data_raises(tmp_path):
    out = tmp_path / "out"
    try:
        write_pack(tmp_path / "empty", out)
        raise AssertionError("应抛出 FileNotFoundError")
    except FileNotFoundError:
        pass
