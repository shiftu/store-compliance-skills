#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_quotes.py — 引文闸门：每条规则的 quote 必须逐字出现在对应来源文件里。

与 validate_rules.py 的分工：
  validate_rules.py  结构 / 枚举 / 日志命中 / 引文（一起查，输出简洁）
  verify_quotes.py   只管引文，输出每条规则的定位信息（文件 + 偏移 + 抓取日），
                     供 CI 与人工复核使用；失败即 exit 1。

检查项：
  1. quote 长度 40–300 字符
  2. source_url 能在 sources/ 里找到抓取文件（按文件头 `<!-- source: URL`）
  3. quote 必须在原始文本里**逐字**出现（不剥 markdown、不折叠空白、不改撇号）。
     这是评审要求的硬口径：跨 `[链接](url)` / `**加粗**` 的句子必须截到标记之外。
     `--lenient` 才退回「归一化后命中」的宽松比对（仅用于诊断）。
  4. retrieved_on 必须等于该 URL 在抓取日志中的成功日期（不许凭记忆填）
  5. retrieved_on 必须不晚于 verified_on

用法：
  python3 rules/verify_quotes.py                # 两个目录全查
  python3 rules/verify_quotes.py --json         # 机器可读
  python3 rules/verify_quotes.py rules/play_rules.json -v
"""
import argparse
import glob
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(BASE, "_logs", "fetch_2026-11-23.jsonl")
if not os.path.exists(LOG):
    _c = sorted(glob.glob(os.path.join(BASE, "_logs", "fetch_*.jsonl")))
    LOG = _c[-1] if _c else LOG

def sources_root():
    """官方原文快照目录：新包在 rules/sources/，旧布局在 sources/。"""
    for cand in (os.path.join(BASE, "rules", "sources"), os.path.join(BASE, "sources")):
        if os.path.isdir(cand):
            return cand
    return os.path.join(BASE, "rules", "sources")

CATALOGS = sorted(glob.glob(os.path.join(BASE, "rules", "*_rules.json")))
MIN_QUOTE, MAX_QUOTE = 40, 300
# 条款里的操作句本身很短（它是「这句话就是义务」的情形），单独放行到 30 字符
SHORT_OK = {"ASRG-5.1.1v-ACCOUNT-DELETE": 30}


def norm(s):
    s = s.replace("\u00a0", " ").replace("\u200b", "")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("…", "...")):
        s = s.replace(a, b)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)      # markdown 链接 -> 链接文字
    s = re.sub(r"[*_`|~#>\[\]]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def source_map():
    out = {}
    for p in glob.glob(os.path.join(sources_root(), "*", "*.md")):
        head = open(p, encoding="utf-8").read(800)
        m = re.search(r"source: (\S+)", head)
        if m:
            out.setdefault(m.group(1).rstrip("/"), []).append(p)
    return out


def log_dates():
    """url -> {'date': 首个成功抓取日, 'statuses': {...}}"""
    out = {}
    if not os.path.exists(LOG):
        return out
    for line in open(LOG, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        url = (d.get("query_or_url") or "").rstrip("/")
        rec = out.setdefault(url, {"date": None, "statuses": set()})
        rec["statuses"].add(d.get("status"))
        if d.get("status") == "ok" and not rec["date"]:
            rec["date"] = str(d.get("ts", ""))[:10]
    return out


class Checker:
    def __init__(self, lenient=False):
        self.lenient = lenient
        self.srcmap = source_map()
        self.dates = log_dates()
        self._text = {}

    def text(self, path):
        if path not in self._text:
            self._text[path] = open(path, encoding="utf-8").read()
        return self._text[path]

    def check(self, rule):
        rid = rule.get("id", "?")
        quote = rule.get("quote") or ""
        url = (rule.get("source_url") or "").rstrip("/")
        problems, info = [], {}

        lo = SHORT_OK.get(rid, MIN_QUOTE)
        if not (lo <= len(quote) <= MAX_QUOTE):
            problems.append(f"quote 长度 {len(quote)} 不在 {lo}–{MAX_QUOTE}")
        info["chars"] = len(quote)

        files = self.srcmap.get(url) or []
        if not files:
            problems.append(f"未找到抓取文件（source_url={url}）")
            return rid, problems, info
        info["files"] = [os.path.relpath(f, BASE) for f in files]

        hit_file, offset = None, -1
        nq = norm(quote)
        for f in files:
            raw = self.text(f)
            if quote and quote in raw:                 # 严格：原文逐字
                hit_file = f
                offset = raw.find(quote)
                info["mode"] = "raw"
                break
            if self.lenient and nq and nq in norm(raw):
                hit_file = f
                # 归一化前的精确位置：在原始文本里找最长可用片段，用于人工定位
                probe = quote[:60].strip()
                offset = raw.find(probe) if probe else -1
                info["mode"] = "lenient"
                break
        if hit_file is None:
            problems.append("quote 未在原始抓取文本中逐字出现（含 markdown/撇号差异）")
        else:
            info["file"] = os.path.relpath(hit_file, BASE)
            info["raw_offset"] = offset

        rec = self.dates.get(url)
        if not rec:
            problems.append("source_url 不在抓取日志里")
        elif "ok" not in rec["statuses"]:
            problems.append(f"source_url 日志状态非 ok：{sorted(rec['statuses'])}")
        else:
            got = rule.get("retrieved_on")
            if got != rec["date"]:
                problems.append(f"retrieved_on={got} 与日志抓取日 {rec['date']} 不一致")
            v = rule.get("verified_on") or ""
            if got and v and got > v:
                problems.append(f"retrieved_on={got} 晚于 verified_on={v}")
        info["retrieved_on"] = rule.get("retrieved_on")
        return rid, problems, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("catalogs", nargs="*", default=CATALOGS)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--lenient", action="store_true",
                    help="允许归一化（去 markdown / 折叠空白）后命中；默认关闭")
    a = ap.parse_args()

    ck = Checker(lenient=a.lenient)
    results, fails = [], 0
    for path in a.catalogs:
        cat = json.load(open(path, encoding="utf-8"))
        for r in cat.get("rules", []):
            rid, problems, info = ck.check(r)
            if problems:
                fails += 1
            results.append({"catalog": os.path.basename(path), "id": rid,
                            "ok": not problems, "problems": problems, **info})

    if a.json:
        print(json.dumps({"checked": len(results), "failed": fails, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        for x in results:
            if x["ok"]:
                if a.verbose:
                    print(f"  PASS {x['id']:<28} {x['chars']:>3}c  {x['file']}  @{x.get('raw_offset')}")
            else:
                print(f"  FAIL {x['id']:<28} " + "｜".join(x["problems"]))
        by_cat = {}
        for x in results:
            c = by_cat.setdefault(x["catalog"], [0, 0])
            c[0] += 1
            c[1] += 0 if x["ok"] else 1
        print()
        for c, (n, bad) in by_cat.items():
            print(f"== {c}: {n} quotes, {bad} failed")
        print(f"\nRESULT: {'ok' if fails == 0 else 'FAIL'} ({len(results)} quotes, {fails} failed)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
