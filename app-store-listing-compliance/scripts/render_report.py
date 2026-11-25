#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_report.py — 由 listing.json + verdicts.json 生成 report.md（固定五段结构）。

用法：
  render_report.py <out_dir> <slug>
  render_report.py <out_dir> --all

报告只陈述：判定、法条原句、证据文件里的逐字子串、后果、修法、核实边界。
不写「会不会通过审核」这类预测。
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_run import effective_severity  # noqa: E402

SEV_ORDER = {"removal": 0, "rejection": 1, "advisory": 2}
SEV_LABEL = {"removal": "下架级", "rejection": "拒审级", "advisory": "整改建议"}
STORE_LABEL = {"apple_app_store": "App Store", "google_play": "Google Play"}


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def catalog_for(skill_dir, store):
    want = "apple_rules.json" if store == "apple_app_store" else "play_rules.json"
    p = os.path.join(skill_dir, "rules", want)
    if os.path.exists(p):
        return p
    c = glob.glob(os.path.join(skill_dir, "rules", "*_rules.json"))
    return c[0] if len(c) == 1 else None


def default_verifier(rule, store):
    obs = rule.get("observability")
    obs = " ".join(obs) if isinstance(obs, list) else str(obs or "")
    if "listing" in obs or "policy" in obs:
        return "Play Console 后台" if store == "google_play" else "App Store Connect 后台"
    return "安装包或实机"


def cell(s, limit=120):
    s = ("" if s is None else str(s)).replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= limit else s[:limit] + "…"


def render(skill_dir, out_dir, slug):
    app_dir = os.path.join(out_dir, slug)
    listing = load(os.path.join(app_dir, "listing.json"))
    trial = load(os.path.join(app_dir, "verdicts.json"))
    cat = load(catalog_for(skill_dir, listing.get("store")))
    rules = {r["id"]: r for r in cat["rules"]}
    upcoming = {rid for rid, r in rules.items() if r.get("status") == "upcoming"}
    s = trial.get("summary") or {}
    app = listing.get("app") or {}
    store = STORE_LABEL.get(listing.get("store"), listing.get("store"))
    countries = listing.get("countries") or []

    L = []
    A = L.append
    title = app.get("name") or slug
    A("# %s · %s 合规实测报告" % (title, store))
    A("")
    import datetime
    vo = cat.get("verified_on") or ""
    try:
        age = (datetime.date.fromisoformat(listing.get("fetched_on") or "2026-01-01")
               - datetime.date.fromisoformat(vo)).days
    except Exception:
        age = None
    if age is not None and age > 60:
        A("> ⚠️ 规则库可能过期：`verified_on` = %s，距抓取日 %d 天；先跑 `scripts/refresh_sources.sh` 复核再采信结论。" % (vo, age))
        A("")
    ident = listing.get("input")
    A("- 应用：%s（%s：`%s`）" % (title, "Apple ID" if listing.get("store") == "apple_app_store"
                                else "包名", ident))
    A("- 商店：%s（%s）" % (store, " / ".join(c.upper() for c in countries) or "us"))
    A("- 开发者：%s" % (app.get("developer") or app.get("seller") or "未取到"))
    A("- 抓取日：%s · HTTP 请求 %s 次 · 证据文件 %d 份"
      % (listing.get("fetched_on"), listing.get("requests"), len(listing.get("evidence_files") or [])))
    A("- 判定口径：`%s`（生效 %d 条；upcoming %d 条不进风险等级，单列于第 4 段）"
      % (os.path.basename(catalog_for(skill_dir, listing.get("store"))),
         len(rules) - len(upcoming), len(upcoming)))
    A("")
    A("**风险等级：%s**" % (s.get("risk") or "未计算"))
    A("")
    if listing.get("status") == "delisted":
        A("> 商店页返回 404：该应用在当前店面已下架（这是结论本身，不是抓取故障）。")
        A("")

    # ---------- 1
    A("## 1. 结论")
    A("")
    A("| 项 | 数量 |")
    A("|---|---|")
    for k in ("total", "符合", "不符合", "无法从外部判断", "不适用"):
        A("| %s | %s |" % (k, s.get(k)))
    A("")
    vbs = s.get("violations_by_severity") or {}
    A("不符合按等级：下架级 %d 条、拒审级 %d 条、整改建议 %d 条。"
      % (len(vbs.get("removal") or []), len(vbs.get("rejection") or []), len(vbs.get("advisory") or [])))
    A("")
    A("合计 %s 条：%s 条无违规证据，%s 条不符合，%s 条外部无法核实，%s 条前提不成立。"
      % (s.get("total"), s.get("符合"), s.get("不符合"), s.get("无法从外部判断"), s.get("不适用")))
    A("")

    vs = [v for v in trial["verdicts"] if v["rule_id"] not in upcoming]

    # ---------- 2
    A("## 2. 阻断项（下架级）")
    A("")
    block = sorted([v for v in vs if v["verdict"] == "不符合"
                    and effective_severity(rules[v["rule_id"]], v) == "removal"],
                   key=lambda v: v["rule_id"])
    if not block:
        A("本店未发现下架级阻断项（判定范围见文末「方法与边界」）。")
    for v in block:
        r = rules[v["rule_id"]]
        A("### %s %s" % (r["id"], r["title"]))
        A("")
        A("- 结论：**%s**（置信度 %s）" % (v["verdict"], v["confidence"]))
        A("- 条号：%s · 来源 %s" % (r.get("section"), r.get("source_url")))
        if r.get("quote"):
            A("- 原文：“%s”" % r["quote"])
        for e in v.get("evidence") or []:
            if "find" in e:
                A("- 证据：`%s` 含“%s”" % (e["file"], e["find"].replace("\n", " ")[:160]))
            elif "absent" in e:
                A("- 证据：`%s` 中不存在“%s”（%s）" % (e["file"], e.get("absent"), e.get("note", "")))
        A("- 后果：%s" % ("提交不通过 / 已上架会被移除" if r.get("severity") == "removal" else "审核受阻"))
        A("- 判定说明：%s" % v.get("note", ""))
        if r.get("fix"):
            A("- 修法：%s" % r["fix"])
        A("")

    # ---------- 3
    A("## 3. 疑似违规（拒审级 / 整改建议）")
    A("")
    sus = sorted([v for v in vs if v["verdict"] == "不符合"
                  and effective_severity(rules[v["rule_id"]], v) in ("rejection", "advisory")],
                 key=lambda v: (SEV_ORDER.get(effective_severity(rules[v["rule_id"]], v), 3), v["rule_id"]))
    if not sus:
        A("本店未发现疑似违规项。")
    for v in sus:
        r = rules[v["rule_id"]]
        A("### %s %s" % (r["id"], r["title"]))
        A("")
        A("- 结论：**%s**（置信度 %s，%s）"
          % (v["verdict"], v["confidence"],
             SEV_LABEL.get(effective_severity(r, v), effective_severity(r, v))))
        if effective_severity(r, v) != r.get("severity"):
            A("- 等级说明：本条规则库等级为「%s」，本次只发现披露不充分、未发现实质违反，按「%s」处理。"
              % (SEV_LABEL.get(r.get("severity"), r.get("severity")),
                 SEV_LABEL.get(effective_severity(r, v), effective_severity(r, v))))
        A("- 条号：%s · 来源 %s" % (r.get("section"), r.get("source_url")))
        if r.get("quote"):
            A("- 原文：“%s”" % r["quote"])
        for e in v.get("evidence") or []:
            if "find" in e:
                A("- 证据：`%s` 含“%s”" % (e["file"], e["find"].replace("\n", " ")[:160]))
            elif "absent" in e:
                A("- 证据：`%s` 中不存在“%s”（%s）" % (e["file"], e.get("absent"), e.get("note", "")))
        A("- 判定说明：%s" % v.get("note", ""))
        if r.get("fix"):
            A("- 修法：%s" % r["fix"])
        A("")

    # ---------- 4
    A("## 4. 即将到期")
    A("")
    dl = trial.get("deadlines") or []
    if not dl:
        A("本规则库当前无 upcoming 条款。")
    else:
        A("| 规则 | 到期日 | 要做的事 | 依据 |")
        A("|---|---|---|---|")
        for d in dl:
            A("| %s | %s | %s | %s |" % (cell(d.get("rule_id"), 40), cell(d.get("due"), 20),
                                         cell(d.get("todo"), 160), cell(d.get("source_url"), 80)))
        A("")
        A("这类条款到期即按生效规则判，不能算「符合」；到期前未整改会在下一版审核时触发。")
    A("")

    # ---------- 5
    A("## 5. 无法核实")
    A("")
    unk = [v for v in vs if v["verdict"] == "无法从外部判断"]
    na = [v for v in vs if v["verdict"] == "不适用"]
    if unk:
        A("| 规则 | 等级 | 为何判不了 | 谁能核实 |")
        A("|---|---|---|---|")
        for v in sorted(unk, key=lambda v: v["rule_id"]):
            r = rules[v["rule_id"]]
            A("| %s | %s | %s | %s |" % (cell(r["id"], 44),
                                         SEV_LABEL.get(r.get("severity"), r.get("severity")),
                                         cell(v.get("note"), 220),
                                         cell(v.get("verified_by") or default_verifier(r, listing.get("store")), 60)))
        A("")
    else:
        A("无「无法从外部判断」条目。")
        A("")
    if na:
        A("前提不成立（不适用）：" + "；".join(
            "%s %s" % (v["rule_id"], (v.get("note") or "").split("，")[0][:40])
            for v in sorted(na, key=lambda v: v["rule_id"])))
        A("")

    # ---------- 附
    A("## 附：证据清单")
    A("")
    for e in listing.get("evidence_files") or []:
        A("- `%s` ← %s（%s）" % (e.get("file"), e.get("url"), e.get("kind")))
    ext = [x for x in (trial.get("sources") or []) if x.get("external")]
    if ext:
        A("")
        A("外部页面（非本 App 官方）来源：")
        for src in ext:
            A("- `%s` ← %s" % (src.get("file"), src.get("url")))
    A("")
    A("## 方法与边界")
    A("")
    A("- 取数：`scripts/fetch_listing.py`，每个 HTTP 请求一行日志（`%s`），原始响应与可见文本都留档在 `_raw/`。"
      % (listing.get("log") or "_logs/fetch_*.jsonl"))
    A("- 判定：route=script 的条目由脚本直接定论（字段解析 + 逐字比对）；route=llm 与 needs_binary 的条目由模型按规则库 `verify` 步骤判定，"
      "人工只需复核结论与证据。")
    A("- 证据口径：`find` 是 `_raw` 文件里的逐字子串，`absent` 是机械确认的缺失；不带这两者的断言不允许出现在报告里。")
    A("- 边界：应用内行为（弹窗、同意记录、年龄门、支付流程、内容过滤）无法从商店页取到，落在第 5 段，需要安装包、实机或后台。")
    A("- 本报告不预测审核结果，只给证据、法条后果与修法。")
    A("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    slugs = ([os.path.basename(os.path.dirname(p)) for p in
              glob.glob(os.path.join(a.out_dir, "*", "listing.json"))] if (a.all or not a.slug)
             else [a.slug])
    for slug in sorted(slugs):
        md = render(skill_dir, a.out_dir, slug)
        out = os.path.join(a.out_dir, slug, "report.md")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(md)
        print("[render_report] %s (%d chars)" % (out, len(md)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
