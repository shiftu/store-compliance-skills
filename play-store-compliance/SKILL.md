---
name: play-store-compliance
description: "用公开证据逐条判 Android App 是否违反 Google Play 开发者政策（隐私与 Data safety、订阅披露、IARC 分级、匿名聊天年龄限制、AI 内容、结算）。Use when asked 查 Google Play 合规风险 / 下架风险 / Data safety 与政策是否一致."
version: 1.0.0
author: shiftu
platforms: [macos, linux]
prerequisites:
  commands: [python3, hermes]
---

# play-store-compliance — Google Play 上架合规判定

对**已上架**的 Android App 逐条判定 Google Play 开发者政策与商店页要求（隐私政策与 Data safety、订阅披露、IARC 内容分级、匿名/随机聊天类年龄限制、AI 生成内容、Play 结算、EEA 交易者声明）。

**判的是公开可见证据，不是审核结果。** 没有源码、没有 Play Console 权限；需要安装包或后台才能确认的条款一律 `无法从外部判断` 并写清「需要什么」。

规则库 37 条（`rules/play_rules.json`），政策时间表 `rules/play_deadlines.json`（15 条公告变更，含「无对应规则」标注），官方原文快照 `rules/sources/play/`。

## 触发场景

- 「这款 Android App 在 Google Play 有什么合规风险 / 会不会被下架」
- 「Data safety 声明与隐私政策对不对得上」「订阅披露够不够」
- 「分级是 Teen 但内容是约炮/成人向，有没有问题」
- 批量自查里的 Android 部分

## 一条命令跑完

```bash
scripts/run_app.sh <包名 或 play.google.com URL> <out_dir> [app 名称] [judge]
```

例：`scripts/run_app.sh com.example.app runs ExampleApp`

第 4 参数写 `judge` 表示跳过取数、只用已有 `_raw/` 重跑判定。

| 步骤 | 命令 | 产物 |
|---|---|---|
| 1 取数 | `scripts/fetch_listing.py <package> <out_dir> [--countries us,de]` | `_raw/*`、`listing.json`、`script_verdicts.json`、`_logs/fetch_<date>.jsonl` |
| 2 判定 | `run_app.sh` 内置：拼 prompt → `hermes chat --query-file` → 合并 | `_raw/prompt.md`、`verdicts.json` |
| 3 闸门 | `scripts/check_run.py <out_dir> <slug>` | 退出码（0 = 全过） |
| 4 报告 | `scripts/render_report.py <out_dir> <slug>` | `report.md`（五段） |

## 硬性规则（违反即失败）

1. **只写查到的。** 每条判定挂证据：`find`（`_raw` 快照里的**逐字子串**）或 `absent`（机械确认的缺失 + 为什么该缺失算证据）。
2. **`不符合` 必须有正面证据。** 「页面上没看到」不能判违规——降级 `无法从外部判断` 并写清缺什么。
3. **`不适用` ≠ `符合`。** 前提不成立（无该功能 / 未加入 Families / 无健康声明）写 `不适用` 并给证据，不得记成 `符合`。
4. **先过闸门再汇报。** `check_run.py` 输出 `RESULT: ok` 才算完成。
5. **404 是结论不是故障。** 商店页 404 写 `status=delisted`（下架本身就是要的报告结论），退出码 0；此时仍按现有证据逐条判，取不到的一律 `无法从外部判断`，不要因为下架就把所有条目写成 `不适用`。
6. **绝不预测结果。** 只给「哪条不符合 + 证据 + 条款后果 + 怎么改」。
7. **未生效条款不算违规。** `status=upcoming` 只进 `deadlines[]`（如 GP-SUB-05 资格类折扣 2027-01-27、GP-TRADER-01-DSA 2027-02-01）。
8. **规则库超 60 天要声明。** 报告首段后自动插 `⚠️ 规则库可能过期`；先跑 `scripts/refresh_sources.sh` 复核。

## 取数拿到什么

Play 侧 5–7 个请求（带 `CONSENT=YES+cb` cookie 与桌面 UA）：

- `play.google.com/store/apps/details?id=<pkg>&hl=en&gl=US`（+ EEA 店面如 `hl=de&gl=DE`）— 标题、开发者、评分、下载量、`Updated on`、`In-app purchases`、IARC 分级、`Users Interact` 等标记、`About this app` 描述、隐私政策链接
- `play.google.com/store/apps/datasafety?id=<pkg>` — Data safety：Data shared / Data collected / Security practices 三段与数据类别
- `App support` / `About the developer` 块 — 支援邮箱、电话、地址
- 隐私政策页、条款页（只认应用自有域名，`google.com` / `gstatic` 的页脚链接不算）

每个请求写一行 `_logs/fetch_<date>.jsonl`。**没有日志行的 URL 不得出现在 `sources[]`。** 只依赖 Python 标准库。

`listing.json` 契约见 `references/schema.md`。

## 怎么判（route）

| route | 已定论 | 怎么判 |
|---|---|---|
| `script` | 9 条由 `fetch_listing.py` 直接定论 | 标题长度/emoji/排名宣称、隐私链接 200 且非 Google 站内、Data safety 三段齐全、IARC 分级与政策自述年龄冲突、Families 计划、健康免责、Play 结算、匿名聊天类年龄门 |
| `llm` | 读政策/条款/描述做语义比对 | Data safety 与政策逐项一致性、显著披露与同意、删号双通道、订阅五要素、元数据精确性、UGC 审核、AI 举报与防护 |
| `vision` | 截图/图标判读 | 性暗示与血腥素材——没图片一律 `无法从外部判断` |
| `human_only` | 需安装包或 Play Console | 弹窗时机、同意记录、年龄门、订阅权益、广告样式、包名注册与开发者验证 |

**一个常见组合违规**：IARC 分级 `Teen` 而隐私政策自述「intended for adults」——分级与受众矛盾，脚本会直接判 `不符合` 并给出两处证据。

## 政策时间表（`rules/play_deadlines.json`）

15 条公告变更，每条带 `deadline / area / rules[] / summary`：

- `rules[]` 为空且 `unmapped: true` 表示**无对应规则**（如 Contacts 权限政策、SMS/Call Log、前台服务与 geofencing、AppFunctions、Local Network、Manage Contacts、target API level、全量生效基线）——不要硬挂到不相干的规则上。
- 有对应规则的会列 `rule_id`，`run_app.sh` 自动把 `upcoming` 条目写进 `verdicts.json.deadlines`。

## 报告

五段固定顺序（`render_report.py` 生成，不要手写）：结论 → 阻断项（removal）→ 疑似违规（rejection/advisory）→ 即将到期 → 无法核实 + `不适用` 清单。
风险等级按**违规规则的 severity**：removal → 🔴；只有 rejection/advisory → 🟡；无不符合但未知 > 40% → ⚪；否则 🟢。
模板见 `references/report_template.md`，口径与防误报见 `references/judging.md`。

## 维护规则库

```bash
scripts/validate_rules.py rules/play_rules.json
scripts/verify_quotes.py                            # 37 条 quote 逐字回溯 rules/sources/play/
scripts/refresh_sources.sh                          # 重抓 40 份官方页，核对 quote 是否仍存在
```

## 已踩过的坑

- **`Data safety` 页可能整段是单行文本**（无换行），关键词命中即可，不要依赖逐行解析类别。
- **Play 页脚「Privacy Policy • Terms of Service」是 Google 自己的**，不是应用的；只认应用自有域名的链接，否则会把「没有隐私政策」判反。
- **同一款应用的 US 与 EEA 店面价格/条款不同**：订阅本地化要按店面分开看。
- **404 常见**（下架、改名、包名变更），这是结论不是抓取 bug；`listing.json.status=delisted` + 报告写明。
- **`Updated on` 缺失**往往说明页面渲染不完整：相关结论降置信度到「中」，不要判不符合。
- **AI 陪伴类不自动等于「匿名聊天」**：Google 2026-08-26 的扩项针对匿名/随机真人聊天与约会类；AI 角色对话不满足该前提时写 `不适用`，但分级与内容仍可能违反 GP-RATE-01。

## 文件

```
SKILL.md
rules/play_rules.json           37 条规则
rules/play_deadlines.json       15 条政策时间表（含 unmapped 标注）
rules/coverage_ledger.{json,md} 覆盖台账
rules/sources/play/*.md         官方原文快照（40 份）
rules/sources/POLICY_CHANGES.md 政策变更记录
references/schema.md            listing.json / verdicts.json 契约
references/judging.md           判定口径与防误报
references/report_template.md   五段报告模板
references/prompt_template.md   判定 prompt 的契约
scripts/fetch_listing.py        取数（stdlib）
scripts/run_app.sh              一条命令跑完
scripts/check_run.py            闸门
scripts/render_report.py        五段报告
scripts/validate_rules.py       规则库结构校验
scripts/verify_quotes.py        引文逐字闸门
scripts/refresh_sources.sh      官方页复核
_logs/fetch_<date>.jsonl        规则库自身的抓取留痕
```

## 源码仓库

公开仓库：https://github.com/shiftu/store-compliance-skills （两个商店合规 skill 同在此仓库；被问到仓库 / GitHub 地址时回复这个链接）。
