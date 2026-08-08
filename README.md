# Terraria 双语资源包（English / 中文）

在 Terraria（泰拉瑞亚）中**同时显示英文原文和中文翻译**的官方语言资源包。玩游戏的同时学英语，**不需要 tModLoader、不需要任何 Mod、不需要改代码**。

```
物品名：      Copper Shortsword / 铜短剑
NPC 名：      Zombie / 僵尸
Boss 击杀：   Eye of Cthulhu has been defeated! / 克苏鲁之眼已被打败！
成就：        Archaeologist / 考古学家
NPC 对话：    "I can tell you about tools..." / "我可以告诉你关于工具的事……"
```

## 效果预览

> 截图待补充

## 玩家使用方法（不用懂任何技术）

1. **下载**：打开本页右侧的 [Releases](https://github.com/QingGo/terraria-bilin/releases) 页面，下载最新版 `terraria-bilin-v0.1.zip`（**不要解压**，直接使用 zip 文件）。

2. **放入资源包文件夹**：打开文件资源管理器，进入
   `我的文档\My Games\Terraria\ResourcePacks`
   把下载的 zip 文件**原样**放进去（不要删除文件夹里的其他东西）。

   > 找不到「我的文档」？在资源管理器地址栏粘贴 `%USERPROFILE%\Documents\My Games\Terraria\ResourcePacks` 回车。
   > 如果文件夹不存在：先启动一次游戏再关闭，游戏会自动创建；也可以手动新建 `ResourcePacks` 文件夹（注意大小写）。

3. **在游戏内启用**：启动 Terraria → 主菜单 → **资源包**（Resource Packs）→ 在列表中找到 **Terraria Bilingual Pack (EN / 中文)** → 点击 ▶ 移到右侧已启用列表 → 完成。回到游戏立即生效，无需重启。

之后游戏内所有物品、NPC、对话、UI、成就都会以「英文 / 中文」双语显示，**英文在前、中文在后**。

> 游戏语言设为 English 或 简体中文 都同样生效（两种语言文件内容一致）。
> 想恢复单语：在资源包菜单停用即可，立即还原；删除 zip 文件即完全卸载。

## 适合谁

- 想边玩边学英语的玩家
- 想对照中英文本的汉化包玩家
- 英语学习者（物品名、NPC 对话、成就文案都是很好的单词来源）

## 支持范围

| 项目 | 说明 |
|---|---|
| 游戏版本 | Terraria 1.4.5.6（数据直接提取自你的游戏 exe，与版本严格对应） |
| 覆盖内容 | 约 1.5 万条文本双语化（物品/武器/工具提示/NPC/对话/UI/成就/图鉴等） |
| 故意不翻 | 随机世界名词表、制作人员名单、AM/PM 等极短符号（防止生成奇怪名字或界面溢出） |
| 中文显示 | 游戏内置字体原生支持中文，无需安装任何字体 |

## 特性与安全

- **官方机制**：使用 Terraria 官方语言资源包（Language Pack）系统，零 Mod 依赖、可热切换、多人联机客户端本地显示
- **占位符安全**：含变量的文本（如玩家名、击杀数）经一致性检查，双语化不会导致崩溃；占位符不匹配的条目自动保持英文
- **完整验证**：构建产物经 JSON 合法性、key 配对、占位符平衡等全量检查 + 23 项单元测试，并在真实游戏内实测

## 开发者

### 环境

- Python 3.13+，推荐用 [uv](https://docs.astral.sh/uv/) 管理：`uv sync`

### 常用命令

```bash
uv run pytest -q                                    # 单元测试
uv run python src/extract_exe.py                    # 从本地 Terraria.exe 提取语言数据到 _export/
uv run python src/build_pack.py                     # 构建资源包到 output/
uv run python src/verify.py --exe D:\...\Terraria.exe   # 全量验证（含数据新鲜度）
```

发布新版本：打 tag `v0.1` 推送即可，CI 自动 测试 → 构建 → 验证 → 打包 zip 并发布到 GitHub Releases。

### 目录结构

```
docs/           开发方案 + 游戏内实测清单（VERIFY.md）
src/
  extract_exe.py   从 Terraria.exe 提取 12 语言内嵌 JSON（.NET 资源解析）
  policy.py        KeyPolicy：哪些 key 双语 / 保留单语 / 跳过
  bilingualizer.py 配对 + 占位符一致性检查 + 格式决策（短文单行 / 长文双行）
  build_pack.py    生成 pack.json + Content/Localization/*.json + zip
  verify.py        全量验证
tests/          pytest 单元测试
_export/        从游戏提取的语言数据（en-US / zh-Hans + manifest 版本追踪）
output/         生成的资源包（git 忽略，由 CI 构建）
```

### 已知限制

- 不能新增游戏语言选项——本包只是替换现有英文/中文文本
- 少数游戏代码硬编码的文本不走语言文件，无法覆盖
- 随机世界名词表保持英文，避免生成混合语言的世界名
