# Terraria 双语显示 Mod — 开发方案

> 版本：v0.2（整合本地项目调研 + 网络调研后的定稿）
> 日期：2026-08-08
> 目标游戏：Terraria 1.4.5.6（本地已装 `D:\steam\steamapps\common\Terraria`）
> 方案形态：**官方 Language Pack（纯资源包，零 mod / 零 tModLoader / 零代码）**

---

## 1. 结论先行

Terraria **官方原生支持 Language Pack（语言包）**——以资源包（Resource Pack）形式替换任意语言的全部文本，**无需 tModLoader、无需 C#、无需任何 mod**。这是本项目的最优方案，与 `minecraft-bilin`（纯资源包）完全同构，是所有已做双语 mod 中工程量最小的。

```
玩家安装：把 .zip 放入 文档\My Games\Terraria\ResourcePacks\ → 游戏内启用 → 生效
```

对比 stardew-bilin（纯 Content Patcher 数据 patch），Terraria 版连 CP 都省了——**官方原生就是数据替换**。

### 1.1 方案演化过程（调研发现）

| 版本 | 方案 | 发现 | 放弃原因 |
|---|---|---|---|
| v0.1 草案 | tModLoader C# mod + Harmony hook `LanguageManager` | 本地化全走 `Language` API，可 hook | 可行但复杂：需要 tModLoader、C# 工程、Harmony patch、缓存、多人测试 |
| v0.2 定稿 | **官方 Language Pack（资源包）** | 官方指南确认：`Content/Localization/en-US-*.json` 直接替换任意语言文本 | — |

### 1.2 与其它双语 mod 项目对比

| 项目 | 方案形态 | 代码 | 数据源 | 难点 |
|---|---|---|---|---|
| stardew-bilin | Content Patcher 数据 patch | 零 | AssetExporter 从游戏导出 | 字体合并、FNA bug、打字机不可控 |
| minecraft-bilin | 纯资源包（自定义语言） | 零 | Mojang API 下载 client.jar | `%s` 占位符崩溃风险（显式索引重写） |
| civ5-bilin | 改写游戏文本 XML | 零 | 游戏 SQLite 库 | 官方无简中（用繁体）、mod SQL 失败改直改文件 |
| ut-bilin | lang JSON 合并 + 渲染补丁 | 部分（UTMT 补丁） | 好人汉化组 lang | 渲染缩放/气泡高度等大量绘制修复 |
| **terraria-bilin** | **官方 Language Pack** | **零** | **exe 内嵌 JSON / 官方 CSV** | **占位符 `{0}` 双填、`{$}` 引用、KeyPolicy** |

---

## 2. 技术调研结论（已核实）

### 2.1 官方 Language Pack 机制（核心事实，官方指南确认）

- **资源包结构**：`pack.json` + `Content/Localization/` 文件夹
- **语言文件命名**：`{语言前缀}-任意名.json` 或 `.csv`，如 `en-US-Bilingual.json`、`zh-Hans-Localization.json`
- **语言前缀**（官方 9 种，exe 内实测 **11 种**含 ja-JP/ko-KR/zh-Hant）：`en-US, de-DE, it-IT, fr-FR, zh-Hans, es-ES, ru-RU, pt-BR, pl-PL`（+ ja-JP, ko-KR, zh-Hant）
- **JSON 格式**（双层嵌套，与语言包一致）：
  ```json
  {
    "ItemName": { "CopperShortsword": "Copper Shortsword / 铜短剑" },
    "ItemTooltip": { "ToiletCactus": "'...' / '...'" }
  }
  ```
- **CSV 格式**：`Key,Translation` 两列，key 为 `Category.Key`（如 `ItemName.CopperShortsword`）
- **生效方式**：游戏内 主菜单 → 创意工坊 → 使用资源包 启用/停用（可热切换，无需重启）；与其它包冲突时按优先级（顶部优先）
- **替换语义**：只替换列出的 key，未列出的保持原样——**天然支持"部分双语"**（只改想改的类别）
- **安装**：手动（`Documents\My Games\Terraria\ResourcePacks\`，支持文件夹或 zip）或 Steam Workshop

### 2.2 支持的高级语法（占位符，官方指南确认）

| 语法 | 含义 | 双语用法 |
|---|---|---|
| `{0}` `{1}` | 动态参数（运行时填入玩家名/敌人名/数字等） | **两侧各保留一份**：`"{0} has defeated {1} / {0} 击败了 {1}"` → 运行时两侧各填一次，正确 |
| `{$Category.Key}` | 引用其它 key 的文本（Common Tooltip 等） | 保留引用；若被引用 key 也双语化了，引用处自动显示双语 |
| `<right>` `<left>` | 键位输入占位 | 保留，游戏自动替换 |
| `\n` | 换行 | 长文本用 `EN\n中文` 双行 |
| `[c/color:text]` | 彩色文本 | 保留 |

**关键：`{0}` 双填安全性**。与 Minecraft 的 `%s`（Java 顺序消费，翻倍必崩）不同，Terraria 的 `{0}` 是 C# `string.Format` 命名索引——两侧各写一份 `{0}`，运行时传 1 个参数，C# 会**在同一参数上重复引用**，天然安全。这是本方案占位符处理的最大简化。

### 2.3 已知限制（官方指南确认，决定 KeyPolicy 设计）

1. **不能添加新语言**到语言菜单——只能替换现有语言。本方案不需要新语言（替换 en-US 为 `EN / 中文` 即可）
2. **不能添加新动态参数**——只能调整已有 `{0}` 的位置/数量。本方案遵守
3. **不能添加新 Common Tooltip 引用**——只能改已有引用指向的文本
4. **不能添加字符集**——但中文/日文/韩文都是官方语言，字形全支持（1.4.4+ 统一 DynamicSpriteFont）

### 2.4 数据源（已实测验证）

| 数据源 | 位置 | 状态 |
|---|---|---|
| **本地 exe 内嵌 JSON** | `Terraria.exe` 内 `.NET 资源流`（实测 `Iron Pickaxe` 文本在 12.7MB 偏移处；资源名 `Terraria.Localization.Content.{lang}.{Category}.json`） | ✅ 已实测存在，**零外部依赖，与游戏版本严格一致** |
| 官方 All Localizations.csv | 官方指南附件（6.5MB，全部语言全部 key 一行一条） | 备选，需从论坛下载 |
| tModLoader 仓库 | `patches/tModLoader/Terraria/Localization/Content/{culture}/`（仅 TML 自己的文本 + Main.json.patch 差分） | 参考（原版全量不在公开路径） |

### 2.5 字体（无 Stardew 版 FNA bug 风险）

- Terraria 1.4.4+ 使用 `DynamicSpriteFont`（ReLogic.Graphics），**语言无关统一字体**：`Content/Fonts/` 下仅 5 个字体 XNB，无语言后缀
- 官方 11 语言含中文/俄文/波兰文 → 统一字体必然包含全部字形 → **英文语言下渲染中文没问题**（Phase 0 实测确认）
- tModLoader 甚至暴露了 `DynamicSpriteFont.SpriteCharacters`（public 字典）可运行时补字形——本方案用不上，但作为兜底存在

---

## 3. 总体方案

### 3.1 核心思路

生成一个**官方 Language Pack 资源包**，把目标语言（如 en-US）的全部可双语 key 替换为 `EN / 中文` 格式：

```
输出:  terraria-bilingual-pack/
       ├── pack.json                      # {"Name": "...", "Author": "...", "Version": {...}}
       ├── icon.png                       # 可选
       └── Content/Localization/
           ├── en-US-Bilingual.json       # 全部 en 文本 → "EN / 中文"
           └── zh-Hans-Bilingual.json     # 全部 zh 文本 → "中文 / EN"（游戏语言为中文时生效）
```

- 玩家游戏语言 = English → 启用包 → 所有文本显示 `English / 中文`
- 玩家游戏语言 = 中文 → 启用包 → 显示 `中文 / English`（顺序翻转，主语言在前）
- **一个包覆盖两种方向**，与 stardew-bilin 的 `en:zh` / `zh:en` 语义一致

### 3.2 架构图

```
数据源
  Terraria.exe 资源流提取（Python）         官方 All Localizations.csv（备选）
      ↓ 解析 .NET 资源 → 每语言 JSON              ↓
  _export/{lang}/*.json  （Category: {Key: Text}）

构建（Python）
  bilingualizer.py
    ├─ 配对 en/zh 同 key
    ├─ 占位符检查（{0} 双填安全 / {$} 引用保留 / <input> 保留）
    ├─ KeyPolicy 分类（双语 / 单语 / 排除）
    └─ 格式决策（短文本 "EN / 中文" / 长文本 "EN\n中文"）
      ↓
  output/terraria-bilingual-pack/（pack.json + Content/Localization/*.json）
      ↓ 打包 zip
  terraria-bilingual-pack.zip  → 玩家放入 ResourcePacks/ 启用

验证（Python + pytest + CI）
  verify.py：JSON 合法、key 配对、占位符一致性、覆盖统计
```

### 3.3 语言对

- MVP：**en:zh**（en-US + zh-Hans 两个语言文件）
- 官方 11 语言任意可扩展（de:en、ja:zh、ko:zh、zh-Hant 等），只需为每种语言生成对应语言文件
- 复用 stardew 的 `DEFAULT_PAIRS` 单一配置源模式

---

## 4. 核心实现设计

### 4.1 KeyPolicy 分类策略（吸取 stardew 选档界面拥挤教训）

Terraria UI 紧凑，双语文本翻倍有溢出风险。策略表（生成时应用，而非运行时）：

| 策略 | 类别 | 理由 |
|---|---|---|
| **DUAL（双语）** | `ItemName`、`ItemTooltip`、`NPCName`、`NPC*` 对话、`BuffName`、`Achievement*`、`UI` 大部分、`Legacy*` 对话、`DeathText` | 核心学习价值 |
| **SINGLE（单语）** | 战斗飘字、`UI.*` 短标签（如 `WorldSize*`）、快捷键提示、堆叠数字 | 空间敏感/瞬态 |
| **EXCLUDE（跳过）** | 含 `<input>` 键位的超长文本、无法双填的复杂占位符文本 | 安全兜底 |

初版策略表从数据统计生成（analyze_keys.py），人工审核后硬编码，后续加配置。

### 4.2 占位符处理（核心，已确认安全）

```
EN: "{0} has defeated the {1}th {2}!"
ZH: "{0} 击败了第 {1} 个 {2}！"
双语: "{0} has defeated the {1}th {2}! / {0} 击败了第 {1} 个 {2}！"
      ↑ 运行时游戏传 [玩家名, 数字, 敌人名] 3 个参数，C# string.Format 两侧各填一次 → 正确
```

规则：
1. EN/ZH 两侧 `{0..N}` **数量必须一致** → 不一致则该 key 降级为单语（防止 format 异常）
2. `{$Category.Key}` 引用**保留**（游戏自动填被引用文本；若被引用 key 双语化则显示双语）
3. `<right>` 等输入占位保留
4. `\n` 保留；长文本双行布局

### 4.3 格式决策（复用 civ5-bilin 的分层经验）

| 场景 | 格式 |
|---|---|
| 短名词（物品/NPC/buff 名） | `EN / 中文` 单行 |
| tooltip / 短句 | `EN / 中文` 单行 |
| 长文本（>~40 字符或多行 tooltip） | `EN\n中文` 双行 |
| 含 `{$}` 引用文本 | 保留引用结构，引用外层双语文案 |

### 4.4 双语相同时跳过

EN 与 zh 完全相同（专有名词如 "Golf"）→ 保留原值，不拼接（避免 `Golf / Golf`）。

---

## 5. 数据管线（Python 工具）

```
terraria-bilin/
├── docs/                       # 本方案 + roadmap
├── src/
│   ├── extract_exe.py          # 从 Terraria.exe 提取 11 语言 JSON 资源 → _export/
│   ├── download_csv.py         # 备选：官方 All Localizations.csv
│   ├── bilingualizer.py        # en/zh 配对 + 占位符检查 + KeyPolicy + 格式决策
│   ├── build_pack.py           # 生成 pack.json + Content/Localization/*.json + zip
│   ├── analyze_keys.py         # key 类别统计 → KeyPolicy 建议
│   └── verify.py               # 全量验证（见 §6）
├── tests/                      # pytest
├── _export/{lang}/*.json       # 提取数据 + manifest.json（版本追踪）
├── output/                     # 生成的资源包
└── .github/workflows/          # ci.yml + release.yml
```

### 5.1 关键工具

- `extract_exe.py`：解析 `Terraria.exe` 的 .NET 元数据，按资源名 `Terraria.Localization.Content.{lang}.{Category}.json` 提取全部 JSON → `_export/{lang}/`；写 `manifest.json`（gameVersion/dllSha1/exportedAt）
- `bilingualizer.py`：核心引擎（配对/占位符/格式/策略）
- `build_pack.py`：输出资源包 + zip
- `verify.py`：对齐 stardew 的 verify 思路

---

## 6. 测试与 CI

| 层 | 工具 | 覆盖 |
|---|---|---|
| Python 工具层 | pytest | 提取、配对、占位符一致性、格式决策、build 结构（参数化路径，学 stardew 教训） |
| 数据验证 | verify.py | JSON 合法、key 覆盖、占位符平衡、manifest 新鲜度（exe 版本变化告警） |
| 集成 | 游戏内实测清单 | 物品 tooltip / NPC 名 / 对话 / UI / 多人（VERIFY.md） |
| CI | GitHub Actions | pytest + verify + build，tag 发布 zip |

---

## 7. 分阶段路线图

### Phase 0：数据源与可行性验证（1 天）
- [ ] `extract_exe.py` 跑通：从本地 exe 提取 en-US + zh-Hans JSON，确认结构与规模
- [ ] 实测：英文语言下渲染中文（动态字体 CJK 字形）——**最高风险项**
- [ ] 做一个最小语言包（改 5 个 key）→ 放入 ResourcePacks → 游戏内验证生效机制

### Phase 1：MVP（en:zh 资源包）（2-3 天）
- [ ] `bilingualizer.py`（配对/占位符/格式）
- [ ] `build_pack.py`（pack.json + en-US/zh-Hans 双语文件）
- [ ] KeyPolicy v1（ItemName/NPCName/UI/对话 DUAL，空间敏感 SINGLE）
- [ ] verify.py + pytest + CI
- [ ] 游戏内全量截图核对（工具/物品/NPC/对话/UI）

### Phase 2：完善（2 天）
- [ ] 全 11 语言文件（DEFAULT_PAIRS 模式）
- [ ] KeyPolicy 精调（analyze_keys 数据驱动）
- [ ] 多人模式实测（客户端本地化，天然支持）
- [ ] Steam Workshop 发布准备（pack.json 元数据 + 图标）

### Phase 3：发布（1 天）
- [ ] README（中文，含安装/切换/已知限制）
- [ ] GitHub Release（zip）+ Steam Workshop
- [ ] 已知限制文档化

---

## 8. 风险与对策

| # | 风险 | 等级 | 对策 |
|---|---|---|---|
| 1 | 英文语言下 CJK 字形缺失 | 低（官方 11 语言含中文，统一字体） | Phase 0 最先实测 |
| 2 | `{0}` 数量两侧不一致 | 低 | verify 强制检查 + 降级单语 |
| 3 | 双语文本过长 UI 溢出 | 中 | KeyPolicy SINGLE + 长文本双行 |
| 4 | exe 资源提取解析失败（.NET 元数据格式） | 中 | 备选：官方 CSV；Phase 0 验证 |
| 5 | 游戏大版本更新（1.4.6+）数据变化 | 中 | manifest 版本追踪 + 重新提取 |
| 6 | `{$}` 引用 key 双语化后的嵌套 | 低 | 接受（与 stardew token 限制同源），verify 统计报告 |

---

## 9. 参考链接

- 官方 Workshop 指南（语言包格式权威来源）: https://forums.terraria.org/index.php?threads/the-ultimate-guide-to-content-creation-and-use-for-the-terraria-workshop.100652/
- tModLoader Localization Wiki: https://github.com/tModLoader/tModLoader/wiki/Localization
- tModLoader 1.4.5 分支（本地化 patch 参考）: https://github.com/tModLoader/tModLoader/tree/1.4.5
- Localizer mod（tModLoader 汉化管理器，参考其反射/Harmony 手法）: https://github.com/chi-rei-den/Localizer
- MoreLocales mod（自定义文化注册，若未来需要新语言）: https://github.com/queueAngel/MoreLocales

---

## 10. 与其它项目的可复用资产

| 来源 | 复用点 |
|---|---|
| stardew-bilin | verify 检查思路、DEFAULT_PAIRS 模式、CI 工作流、README/已知限制结构 |
| minecraft-bilin | 资源包形态（pack 结构/zip/安装流程）、占位符检查哲学 |
| civ5-bilin | 格式分层（短词单行/长文双行）、KeyPolicy、数据配对逻辑 |
| ut-bilin | policy.json 强制模式（single/zh_only/skip）、溢出收敛报告 |
