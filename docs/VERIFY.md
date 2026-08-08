# VERIFY.md — 游戏内实测清单（MVP 验收）

## 安装

1. 构建 `output\terraria-bilingual-pack.zip`（已由 build_pack.py 生成）
2. 放入 `文档\My Games\Terraria\ResourcePacks\`（无则自建）
3. 游戏内 主菜单 → 资源包（Resource Packs）→ 启用 **Terraria Bilingual Pack (EN / 中文)**
4. 游戏语言 = English → 显示 `English / 中文`；游戏语言 = 中文 → 显示 `中文 / English`

## 生效机制验证（Phase 0 最小项）

- [ ] 热切换：游戏中直接启用/停用资源包，无需重启，文本即时变化
- [ ] 停用后恢复原语言，无残留

## 核心双语项（Phase 1）

- [ ] 物品名：铜短剑 tooltip 与背包悬浮显示 `Copper Shortsword / 铜短剑`
- [ ] 物品 tooltip：长文本（如天顶剑）双行显示，英文与中文各自独立成行
- [ ] NPC 名：僵尸头顶与图鉴显示 `Zombie / 僵尸`
- [ ] Boss 击败横幅：`{0} has been defeated! / {0}已被打败！` 玩家名两侧各填一次
- [ ] NPC 对话：向导/商人对话框双语文案
- [ ] 成就：名称与描述双语
- [ ] UI 按钮与玩家创建界面的短标签（Play/Back/Eyes/眼睛等）均已双语
- [ ] 仅 AM/PM/HP/MP 等 <=3 字符符号保持英文（SINGLE 策略）

## 占位符专项

- [ ] 多条参数文本（`{0}` `{1}` `{2}`）：如击杀信息，双侧各自填入且无 Format 异常
- [ ] 命名占位符（`{PlayerName}` 等）：对话中正常替换
- [ ] 键位提示（`<right>`）：保留且正常显示
- [ ] 含 `{$}` 引用的文本（如 CommonItemTooltip）：正常解析

## 布局风险检查

- [ ] 物品行 2 倍长文本在 800x600 低分辨率下无溢出/截断
- [ ] NPC 头顶名字双语无重叠
- [ ] 背包/箱子 UI 中物品名悬浮提示完整显示
- [ ] 深度计/罗盘等 HUD 短标签正常（SINGLE 保留）

## 已知的刻意跳过项（非 bug）

- `Key`/`Language`/`CLI`/`EmojiCommand`/`Controls`：自引用或内部文本，跳过
- `RandomWorldName_*`：随机世界名词表，避免生成怪异世界名
- `CreditsRollCategory_*`：制作人员名单
- UI/GameUI 极短符号（<=3 字符如 AM/PM，无空格）保留英文
- en/zh 完全相同的文本（专有名词如宠物名）
- 占位符集合不一致的 key（官方 zh 数据自身 bug，如 `ItemTooltip.RubblemakerLarge`）

## 多人模式（Phase 2 预检）

- [ ] 客户端本地化：进入他人服务器，本地显示双语，对方语言不受影响

## 回归检查

- [ ] `uv run pytest` 全绿
- [ ] `uv run python src/verify.py --exe D:\steam\steamapps\common\Terraria\Terraria.exe` 通过
