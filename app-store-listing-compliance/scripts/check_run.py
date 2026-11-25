#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""check_run.py — 判定闸门。任一条不过即非零退出。

用法：
  check_run.py <out_dir> <slug>            校验单款（含 report.md 五段）
  check_run.py <out_dir> --all             校验 out_dir 下所有 *\listing.json
  check_run.py <out_dir> <slug> --pre-render   出报告前先过一遍（跳过报告段检查）
  check_run.py <out_dir> <slug> --report-only  只查报告段

闸门清单（全部机械可执行）：
  1. 目录里必须有 listing.json 与 verdicts.json
  2. 每个 rule_id 存在于规则库；规则库每条都有且只有一条结论
  3. verdict ∈ {符合, 不符合, 无法从外部判断, 不适用}；confidence ∈ {高, 中, 低}
  4. 每条 find 证据必须是对应 _raw 文件里的**逐字子串**（不折叠空白、不改撇号、
     不剥 markdown）；每条 absent 证据必须在该文件里确实不存在
  5. 不符合 必须有至少一条 find 证据；不适用 必须给证据说明前提不成立
  6. status=upcoming 的规则不进风险等级，且必须出现在 deadlines[]
  7. summary 的计数/风险等级必须与 verdicts 重算结果一致
  8. 抓取日志行数 ≥ listing.json 记录的请求数
  9. report.md 含五段固定结构，且不出现「会通过 / 会被拒」这类预测
"""
import argparse
import glob
import json
import os
import sys

VERDICTS = {"符合", "不符合", "无法从外部判断", "不适用"}
CONF = {"高", "中", "低"}
SEV = {"removal", "rejection", "advisory"}
RISK_BY_SEV = {"removal": "🔴 高风险", "rejection": "🟡 有条件", "advisory": "🟡 有条件"}
SECTIONS = ["## 1. 结论", "## 2. 阻断项", "## 3. 疑似违规", "## 4. 即将到期", "## 5. 无法核实"]
FORBIDDEN = ["会通过", "会被拒", "大概率过", "一定会过", "建议直接上架", "审核通过率"]


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def catalog_for(skill_dir, store):
    want = "apple_rules.json" if store == "apple_app_store" else "play_rules.json"
    p = os.path.join(skill_dir, "rules", want)
    if os.path.exists(p):
        return p
    cand = glob.glob(os.path.join(skill_dir, "rules", "*_rules.json"))
    return cand[0] if len(cand) == 1 else None


SEV_RANK = {"removal": 0, "rejection": 1, "advisory": 2}


def effective_severity(rule, verdict):
    """结论可以把等级往轻里调（severity_override），不能往重里调。"""
    base = rule.get("severity")
    ov = (verdict or {}).get("severity_override")
    if ov in SEV_RANK and base in SEV_RANK and SEV_RANK[ov] > SEV_RANK[base]:
        return ov
    return base


def evidence_errors(app_dir, v, sources, cache=None):
    """单条结论的证据问题清单（空 = 证据站得住）。闸门与自动降级共用这一份逻辑。"""
    cache = {} if cache is None else cache
    errs, finds = [], 0
    for e in v.get("evidence") or []:
        rel = e.get("file")
        if not rel:
            errs.append("证据缺 file")
            continue
        if sources and rel not in sources:
            errs.append("证据文件不在 sources[] 里：%s" % rel)
        if rel not in cache:
            p = os.path.join(app_dir, rel)
            cache[rel] = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else None
        body = cache[rel]
        if body is None:
            errs.append("证据文件不存在：%s" % rel)
            continue
        if "find" in e:
            finds += 1
            if not e["find"]:
                errs.append("find 为空串")
            elif e["find"] not in body:
                errs.append("find 不是逐字子串（%s）：%r" % (rel, e["find"][:80]))
        elif "absent" in e:
            if e["absent"] and e["absent"] in body:
                errs.append("absent 实际存在（%s）：%r" % (rel, e["absent"]))
            if not (e.get("note") or "").strip():
                errs.append("absent 证据缺 note（为什么要确认缺失）")
        else:
            errs.append("证据必须带 find 或 absent")
    if not (v.get("evidence") or []) and not v.get("demoted_from"):
        errs.append("没有证据")
    if v.get("verdict") == "不符合" and finds == 0 and not v.get("absence_only_violation"):
        errs.append("不符合 必须至少有一条 find 正面证据")
    return errs


def expected_risk(violating_sevs, unknown_ratio, status=None):
    if status == "delisted":
        return "⚫ 已下架"
    if "removal" in violating_sevs:
        return "🔴 高风险"
    if violating_sevs & {"rejection", "advisory"}:
        return "🟡 有条件"
    return "⚪ 待判定（取数能力不足）" if unknown_ratio > 0.4 else "🟢 可上"


def check_app(skill_dir, out_dir, slug, check_report=True):
    app_dir = os.path.join(out_dir, slug)
    errs = []
    lp = os.path.join(app_dir, "listing.json")
    vp = os.path.join(app_dir, "verdicts.json")
    if not os.path.exists(lp):
        return ["%s: 缺 listing.json（先跑 fetch_listing.py）" % slug]
    listing = load_json(lp)
    if not os.path.exists(vp):
        return ["%s: 缺 verdicts.json（判定结果未落盘）" % slug]
    trial = load_json(vp)
    cat_path = catalog_for(skill_dir, listing.get("store"))
    if not cat_path:
        return ["%s: 找不到规则库（rules/*_rules.json）" % slug]
    cat = load_json(cat_path)
    want_store = {"apple_rules.json": "apple_app_store", "play_rules.json": "google_play"}.get(
        os.path.basename(cat_path), cat.get("catalog"))
    if listing.get("store") and want_store and listing["store"] != want_store:
        return None            # 别的店的 App，本技能不管
    rules = {r["id"]: r for r in cat["rules"]}
    upcoming = {rid for rid, r in rules.items() if r.get("status") == "upcoming"}

    # ---- 2. 覆盖：每条规则都要有结论，且不能有规则库外的 id
    verdicts = trial.get("verdicts") or []
    got = {}
    for v in verdicts:
        rid = v.get("rule_id")
        if rid in got:
            errs.append("%s: rule %s 有重复结论" % (slug, rid))
        if rid not in rules:
            errs.append("%s: 结论里的 rule_id 不在规则库：%s" % (slug, rid))
        got[rid] = v
    for rid in rules:
        if rid in upcoming:
            continue          # 未生效条款只进 deadlines[]，不要求判定
        if rid not in got:
            errs.append("%s: 规则库有 %s，但结论里没有" % (slug, rid))

    # ---- 证据解析
    sources = {s.get("file") for s in (trial.get("sources") or [])}
    cache = {}

    def text_of(rel):
        if rel not in cache:
            p = os.path.join(app_dir, rel)
            cache[rel] = open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else None
        return cache[rel]

    # ---- 3/4/5. 单条结论
    for rid, v in got.items():
        if rid in upcoming:
            continue
        verdict = v.get("verdict")
        if verdict not in VERDICTS:
            errs.append("%s/%s: 非法 verdict %r" % (slug, rid, verdict))
        if v.get("confidence") not in CONF:
            errs.append("%s/%s: 非法 confidence %r" % (slug, rid, v.get("confidence")))
        if not (v.get("note") or "").strip():
            errs.append("%s/%s: note 为空" % (slug, rid))
        for msg in evidence_errors(app_dir, v, sources, cache):
            errs.append("%s/%s: %s" % (slug, rid, msg))
        if v.get("absence_only_violation") and verdict != "不符合":
            errs.append("%s/%s: absence_only_violation 只对 不符合 有效" % (slug, rid))
        if verdict == "不适用" and not (v.get("evidence") or []):
            errs.append("%s/%s: 不适用 也要给证据说明前提为何不成立" % (slug, rid))
        for ly in v.get("layers") or []:
            if ly.get("verdict") not in VERDICTS:
                errs.append("%s/%s: 分层结论非法 %r" % (slug, rid, ly.get("verdict")))
            if not (ly.get("note") or "").strip():
                errs.append("%s/%s: 分层结论缺说明" % (slug, rid))

    # ---- 6. upcoming 必须进 deadlines，且不进计数
    dl = trial.get("deadlines") or []
    dl_ids = [d.get("rule_id") for d in dl]
    for rid in sorted(upcoming - set(dl_ids)):
        errs.append("%s: upcoming 规则 %s 未出现在 deadlines[]" % (slug, rid))
    for d in dl:
        if not d.get("due") or not (d.get("todo") or "").strip():
            errs.append("%s: deadlines 条目缺 due/todo：%r" % (slug, d))

    # ---- 7. summary 重算
    counts = {"符合": 0, "不符合": 0, "无法从外部判断": 0, "不适用": 0}
    violating_sevs = set()
    for rid, v in got.items():
        if rid in upcoming:
            continue
        counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
        if v["verdict"] == "不符合":
            violating_sevs.add(effective_severity(rules[rid], v))
    total = sum(counts.values())
    unknown_ratio = (counts["无法从外部判断"] / total) if total else 0.0
    s = trial.get("summary") or {}
    for k, val in counts.items():
        if s.get(k) != val:
            errs.append("%s: summary[%s]=%r，重算为 %d" % (slug, k, s.get(k), val))
    if s.get("total") != total:
        errs.append("%s: summary[total]=%r，重算为 %d" % (slug, s.get("total"), total))
    if sorted(s.get("upcoming_excluded") or []) != sorted(upcoming):
        errs.append("%s: summary[upcoming_excluded] 与实际 upcoming 不一致" % slug)
    risk = expected_risk(violating_sevs, unknown_ratio, listing.get("status"))
    if s.get("risk") != risk:
        errs.append("%s: summary[risk]=%r，按 severity 重算应为 %r" % (slug, s.get("risk"), risk))
    vbs = s.get("violations_by_severity") or {}
    for sev in SEV:
        want = sorted(rid for rid, v in got.items()
                      if v["verdict"] == "不符合" and rid not in upcoming
                      and effective_severity(rules[rid], v) == sev)
        have = sorted(vbs.get(sev) or [])
        if want != have:
            errs.append("%s: summary[violations_by_severity][%s]=%r，重算为 %r"
                        % (slug, sev, have, want))

    # ---- 8. 日志行数 ≥ 请求数
    req = listing.get("requests")
    log_rel = listing.get("log") or "_logs/fetch_%s.jsonl" % listing.get("fetched_on", "")
    log_path = os.path.join(out_dir, log_rel)
    if req is None:
        errs.append("%s: listing.json 缺 requests（取数脚本未留痕）" % slug)
    elif not os.path.exists(log_path):
        errs.append("%s: 抓取日志不存在：%s" % (slug, log_rel))
    else:
        lines = [x for x in open(log_path, encoding="utf-8").read().split("\n") if x.strip()]
        if len(lines) < int(req):
            errs.append("%s: 日志 %d 行 < 实际请求数 %s" % (slug, len(lines), req))

    # ---- 9. 报告
    if check_report:
        rp = os.path.join(app_dir, "report.md")
        if not os.path.exists(rp):
            errs.append("%s: 缺 report.md（用 render_report.py 生成）" % slug)
        else:
            md = open(rp, encoding="utf-8").read()
            for sec in SECTIONS:
                if sec not in md:
                    errs.append("%s: report.md 缺段 %r" % (slug, sec))
            for bad in FORBIDDEN:
                if bad in md:
                    errs.append("%s: report.md 出现结果预测词 %r（只写证据与后果）" % (slug, bad))
            if listing.get("status") == "delisted" and "已下架" not in md and "delisted" not in md:
                errs.append("%s: listing.status=delisted，但报告未写明已下架" % slug)
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--pre-render", action="store_true")
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    slugs = []
    if a.all or not a.slug:
        slugs = sorted(os.path.basename(os.path.dirname(p))
                       for p in glob.glob(os.path.join(a.out_dir, "*", "listing.json")))
    else:
        slugs = [a.slug]
    if not slugs:
        print("没有任何 listing.json：%s" % a.out_dir)
        return 1

    total = 0
    for slug in slugs:
        errs = check_app(skill_dir, a.out_dir, slug, check_report=not a.pre_render)
        if errs is None:
            print("== %s: 跳过（不属于本店）" % slug)
            continue
        total += len(errs)
        status = "ok" if not errs else "FAIL"
        try:
            t = load_json(os.path.join(a.out_dir, slug, "verdicts.json"))
            s = t.get("summary", {})
            brief = "符合 %s / 不符合 %s / 无法判断 %s / 不适用 %s → %s" % (
                s.get("符合"), s.get("不符合"), s.get("无法从外部判断"), s.get("不适用"), s.get("risk"))
        except Exception:
            brief = ""
        print("== %s: %s  %s" % (slug, status, brief))
        for e in errs:
            print("   FAIL", e)
    print("\nRESULT:", "ok" if total == 0 else "FAIL", "(%d errors, %d apps)" % (total, len(slugs)))
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
