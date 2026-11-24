# 判定 prompt 的契约

`scripts/run_app.sh` 在第 2 步用内联 python 生成 `<app_dir>/_raw/prompt.md`，第 3 步交给
`hermes chat --query-file`。本文件记录 prompt 里**必须存在**的部分，改 prompt 时对照检查。

## 1. 组成（顺序固定）

1. **角色与任务**：判哪一款、工作目录就是 `app_dir`。
2. **硬性规则 7 条**：只判给定 id；`find` 逐字；判不了写 `无法从外部判断`；前提不成立写 `不适用`；
   `不符合` 必须有 `find`（仅「该有的缺失」可 `absence_only_violation`）；置信度三档；只输出 JSON。
3. **应用事实**：`listing.json` 的 `store/input/status/countries/app/links/missing` 摘要（JSON 块）。
4. **脚本已定论的条目**：`script_verdicts.json` 的表格，明确「原样保留，不要重判」——避免模型推翻机械结论，
   也避免同一 `rule_id` 两份结论打架。
5. **证据文本**：`_raw/` 里每个文本快照的全文（单文件上限 9000 字符，总量上限 ~45000），
   带 `### file` + `来源 URL` + `<<< >>>` 围栏。模型只能引用这里出现的文字或自己 `grep` 读到的文字。
6. **待判定规则**：每条给 `id / 条号 / severity / observability / requirement / quote / signals / verify / false_positive_notes`。
   `verify` 与 `false_positive_notes` 必须原样进 prompt——它们是「怎么核」和「别误判」的唯一来源。
7. **输出格式示例** + **必须覆盖的 rule_id 全清单**（漏一个就报错）。

## 2. 输出契约

```json
{"verdicts": [
  {"rule_id": "...", "verdict": "符合|不符合|无法从外部判断|不适用",
   "confidence": "高|中|低",
   "evidence": [{"file": "_raw/x.txt", "find": "逐字片段"}],
   "note": "...", "verified_by": "..."}
]}
```

只允许一个 JSON 对象，不要 markdown 代码块。`run_app.sh` 会剥一次 ```json 围栏，再从第一个 `{` 做括号配平截取，
解析失败时把错误写进 `verdicts.json.llm_parse_error` 并让闸门失败——**不要在脚本里静默吞掉解析错误**。

## 3. 生成 prompt 时容易出错的地方

- **截断说明要写进文本里**（「…已截断，需要更多可自行 sed 读取原文件」），否则模型会把省略当「原文没有」。
- **不要把 `.html` / `.json` / `.pdf` 原样塞进 prompt**：`find` 只能对 `.txt` 快照逐字命中；
  HTML 里的标签会让模型抄出对不上的片段。
- **`script` 已判条目要列出来**，而不是「留空让模型跳过」——不列出来模型会重判并在 note 里给出不同说法。
- **`upcoming` 规则不进待判清单**（它们只进 `deadlines[]`）；混进去会让模型把未生效条款判成违规。
- **`status=delisted` 要显式告知**，并要求「按现有证据逐条判，不因为下架就全部写不适用」。
