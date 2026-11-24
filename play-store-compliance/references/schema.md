# 数据契约：`listing.json` / `verdicts.json`（Google Play）

所有产物都是 UTF-8 JSON（`ensure_ascii=False`）。字段名固定，`render_report.py`、`check_run.py` 直接读，不要改名。

## 1. 目录布局

```
<out_dir>/
  _logs/fetch_<YYYY-MM-DD>.jsonl    每次 HTTP 请求一行（append-only）
  <slug>/                           包名把 . 换成 -（com.example.app → com-example-app）
    _raw/                           原始响应 + 可见文本 + prompt.md + llm_output.txt
    listing.json                    取数结果
    script_verdicts.json            route=script 且脚本能定论的条目
    verdicts.json                   全量结论
    report.md                       五段报告
```

## 2. `_logs/fetch_<date>.jsonl`

一行一次真实请求。**没有这一行的 URL 不得出现在 `sources[]` 里**：

```json
{"ts":"2026-11-24T01:20:03-0600","tool":"fetch",
 "query_or_url":"https://play.google.com/store/apps/datasafety?id=com.example.app&hl=en&gl=US",
 "status":"ok|blocked|empty|delisted","used_for":"Play Data safety (us)","note":"http 200"}
```

`check_run.py` 校验：日志行数 ≥ `listing.json.requests`。

## 3. `listing.json`

```json
{
  "store": "google_play",
  "input": "com.example.app",
  "slug": "com-example-app",
  "status": "ok",                    // ok | delisted（404/410）
  "fetched_on": "2026-11-24",
  "countries": ["us", "de"],
  "requests": 5,
  "log": "_logs/fetch_2026-11-24.jsonl",
  "app": {"name": "...", "developer": "Example Developer Ltd", "rating": "2.4",
          "rating_count": "11", "downloads": "1K+", "updated": "Nov 20, 2026",
          "iap": true, "content_rating": "Teen"},
  "fields": {"<字段>": {"value": ..., "source": "_raw/xxx.txt"}},
  "links": {"privacy": {"url": "https://example.com/privacy",
                        "http": 200, "file": "_raw/..._privacy.txt", "pdf": false},
            "terms": {...}},
  "pages": {"us": {"title": "...", "developer": "...", "rating": "2.4",
                   "content_rating": "Teen", "text_file": "_raw/..._play_us.txt",
                   "description": "<About this app 正文>",
                   "support": {"email": "...", "phone": "...", "address": "...", "website": "..."},
                   "links": {"privacy": "...", "terms": "..."},
                   "link_labels": {"privacy": "Privacy Policy"},
                   "data_safety": {"file": "_raw/..._datasafety_us.txt", "http": 200,
                                   "sections": {"shared": true, "collected": true, "security": true},
                                   "categories": ["..."]}}},
  "description_file": "_raw/..._description.txt",
  "evidence_files": [{"file": "_raw/..._play_us.txt", "url": "https://...", "kind": "store_page"}],
  "missing": ["terms"],
  "notes": [],
  "script_rules_done": ["GP-META-01-TITLE"],
  "script_rules_skipped": ["GP-SUB-01-DISCLOSURE"]
}
```

要点：

- `evidence_files[]` 是**唯一合法的证据白名单**：`evidence[].file` 必须是其中某个相对路径。
- 404 → `status=delisted`，并在 `_raw/` 留 `.status` 文件作为证据（下架是结论，退出码仍 0）。
- `links.privacy` 只认应用自有域名；`google.com` / `gstatic` 的页脚链接被过滤掉，`present=false` 时不要当成「有隐私政策」。
- `data_safety` 只取 **us** 店面那份；EEA 那份内容往往一致但字段更少。
- 解析不到的字段写进 `missing[]`，不填猜测值。

## 4. `script_verdicts.json`

`{ "<rule_id>": {"verdict","confidence","evidence":[...],"note"} }`。只含 `route` 带 `script` 且解析成功的条目；`run_app.sh` 原样并入，不要手改。

## 5. `verdicts.json`

```json
{
  "store": "google_play", "app": "com.example.app", "slug": "com-example-app",
  "judged_on": "2026-11-24", "listing_status": "ok",
  "sources": [{"file": "_raw/...", "url": "...", "kind": "store_page", "external": false}],
  "summary": {"符合": 9, "不符合": 1, "无法从外部判断": 12, "不适用": 15, "total": 37,
              "risk": "🟡 有条件",
              "violations_by_severity": {"removal": ["GP-RATE-01-IARC"], "rejection": [], "advisory": []},
              "upcoming_excluded": ["GP-SUB-05-ELIGIBILITY", "GP-TRADER-01-DSA"]},
  "deadlines": [{"rule_id": "GP-TRADER-01-DSA", "due": "2027-02-01", "todo": "...", "source_url": "..."}],
  "verdicts": [
    {"rule_id": "GP-RATE-01-IARC",
     "verdict": "不符合",            // 符合 | 不符合 | 无法从外部判断 | 不适用
     "confidence": "高",
     "evidence": [{"file": "_raw/..._play_us.txt", "find": "Teen"},
                  {"file": "_raw/..._privacy.txt", "find": "intended for adults"}],
     "note": "...", "verified_by": "Play Console 后台"}
  ]
}
```

`upcoming` 的两条（GP-SUB-05 资格类折扣、GP-TRADER-01-DSA 交易者声明）不进计数、不进风险等级，只进 `deadlines[]`。

## 6. 风险等级（`check_run.py` 重算，写错即 FAIL）

| 条件 | 等级 |
|---|---|
| 有 `不符合` 且 severity=removal | 🔴 高风险 |
| 有 `不符合` 且 severity 为 rejection/advisory | 🟡 有条件 |
| 无 `不符合`，`无法从外部判断` 占比 > 40% | ⚪ 待判定（取数能力不足） |
| 无 `不符合`，未知占比 ≤ 40% | 🟢 可上 |

## 7. 证据两条铁律

- `find`：必须是 `_raw` 文件里的**逐字连续子串**，比对时不做任何归一化。
- `absent`：确认该文件里没有这个串，且必须带 `note` 说明「为什么这个缺失构成本条的违反」。`absent` 只能证明「没有」，不能单独证明「错」（`listing.status=delisted` 除外）。
