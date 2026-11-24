#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate rules/apple_rules.json and rules/play_rules.json.

Hard checks (fail = exit 1):
  1. structure: required top-level keys, unique ids, required fields, enums
  2. quote ≤ 300 chars and present *verbatim* in the captured source file whose
     header URL matches the rule's source_url (markdown/typographic noise normalised)
  3. source_url present in _logs/fetch_2026-11-23.jsonl with status=ok
  4. verified_on present and equal to the catalog-level verified_on

Soft checks (warnings): short quotes, quotes that span a truncated region, rules
whose source_url maps to more than one file.

Usage: python3 rules/validate_rules.py [file ...]   (default: both catalogs)
"""
import glob
import json
import re
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(BASE, "_logs", "fetch_2026-11-23.jsonl")
MAX_QUOTE = 300
OBSERVABILITY = {"public_listing", "policy_docs", "binary_only", "console_only", "account_level"}
SEVERITY = {"removal", "rejection", "advisory"}
ROUTE = {"script", "llm", "vision", "human_only"}
STATUS = {"effective", "upcoming"}
SURFACE = {"store_page", "privacy_label", "screenshot", "policy_page",
           "developer_page", "console", "binary"}
CATEGORIES = {"all", "fortune", "ai_companion", "health_mental", "ai_tool", "sub_tool"}


def norm(s: str) -> str:
    s = s.replace("\u00a0", " ").replace("\u200b", "")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("…", "...")):
        s = s.replace(a, b)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)   # markdown links -> link text
    s = re.sub(r"[*_`|~#>\[\]]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def build_source_map():
    """url -> [file paths] from the `<!-- source: URL` header of each captured file."""
    m = {}
    for p in glob.glob(os.path.join(sources_root(), "*", "*.md")):
        head = open(p, encoding="utf-8").read(600)
        hit = re.search(r"source: (\S+)", head)
        if hit:
            m.setdefault(hit.group(1).rstrip("/"), []).append(p)
    return m


def load_log():
    urls = {}
    if not os.path.exists(LOG):
        return urls
    for line in open(LOG, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        urls.setdefault(rec.get("query_or_url", "").rstrip("/"), set()).add(rec.get("status"))
    return urls


def validate(path, srcmap, log):
    errors, warnings = [], []
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return [f"{path}: not valid JSON: {e}"], []
    for k in ("catalog", "store", "verified_on", "source_index", "log", "rules"):
        if k not in data:
            errors.append(f"top-level missing key: {k}")
    top_verified = data.get("verified_on")
    rules = data.get("rules") or []
    if not rules:
        errors.append("no rules")
    seen = {}
    for i, r in enumerate(rules):
        rid = r.get("id", f"<rule #{i}>")
        if rid in seen:
            errors.append(f"duplicate id: {rid}")
        seen[rid] = r
        for f in ("id", "section", "title", "requirement", "quote", "source_url",
                  "effective_or_updated", "observability", "route", "surface", "signals",
                  "verify", "fix", "severity", "status", "categories", "false_positive_notes",
                  "retrieved_on", "verified_on"):
            if not r.get(f):
                errors.append(f"{rid}: missing/empty field {f}")
        if not re.match(r"^(ASRG|GP)-[A-Za-z0-9.\-]+$", rid):
            errors.append(f"{rid}: id must look like ASRG-3.1.2 / GP-SUBS-01")
        obs = r.get("observability")
        obs_list = obs if isinstance(obs, list) else [obs]
        bad_obs = [x for x in obs_list if x not in OBSERVABILITY]
        if bad_obs or not obs_list:
            errors.append(f"{rid}: bad observability {obs!r}")
        if len(obs_list) > 1:
            notes = r.get("observability_notes") or {}
            miss = [x for x in obs_list if not str(notes.get(x, "")).strip()]
            if miss:
                errors.append(f"{rid}: 多层 observability 缺少分层说明 {miss}")
            extra = [k for k in notes if k not in obs_list]
            if extra:
                errors.append(f"{rid}: observability_notes 有多余层 {extra}")
        for fld, allowed in (("surface", SURFACE), ("route", ROUTE)):
            v = r.get(fld)
            v_list = v if isinstance(v, list) else [v]
            if [x for x in v_list if x not in allowed]:
                errors.append(f"{rid}: bad {fld} {v!r}")
            if len(v_list) > 1 and len(v_list) != len(obs_list):
                errors.append(f"{rid}: {fld} 层数 {len(v_list)} 与 observability {len(obs_list)} 不一致")
        if r.get("severity") not in SEVERITY:
            errors.append(f"{rid}: bad severity {r.get('severity')!r}")
        if r.get("status") not in STATUS:
            errors.append(f"{rid}: bad status {r.get('status')!r}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("retrieved_on"))):
            errors.append(f"{rid}: bad retrieved_on {r.get('retrieved_on')!r}")
        if "已用官方原文核实条款" in str(r.get("signals", "")):
            errors.append(f"{rid}: signals 仍是通用模板文字，必须改成该条专属取数")
        if "community_refs" in r:
            refs = [x.strip() for x in str(r["community_refs"]).split(",")]
            for x in refs:
                if not re.fullmatch(r"6\.([1-9]|1[0-9]|2[0-5])", x):
                    errors.append(f"{rid}: bad community_refs item {x!r} (expect 6.1–6.25)")
        cats = r.get("categories") or []
        bad = [c for c in cats if c not in CATEGORIES]
        if bad or not cats:
            errors.append(f"{rid}: bad categories {cats}")
        if r.get("verified_on") != top_verified:
            errors.append(f"{rid}: verified_on {r.get('verified_on')} != catalog {top_verified}")

        q = r.get("quote") or ""
        if len(q) > MAX_QUOTE:
            errors.append(f"{rid}: quote {len(q)} chars > {MAX_QUOTE}")
        if len(q) < 40:
            warnings.append(f"{rid}: quote is only {len(q)} chars — check it is a meaningful excerpt")

        url = (r.get("source_url") or "").rstrip("/")
        if url:
            files = srcmap.get(url)
            if not files:
                errors.append(f"{rid}: source_url has no captured file: {url}")
            else:
                if len(files) > 1:
                    warnings.append(f"{rid}: source_url maps to {len(files)} files ({', '.join(os.path.basename(f) for f in files)})")
                nq = norm(q)
                found = False
                for fp in files:
                    if nq and nq in norm(open(fp, encoding="utf-8").read()):
                        found = True
                        break
                if not found:
                    errors.append(f"{rid}: quote NOT found verbatim in {os.path.basename(files[0])}")
            statuses = log.get(url)
            if not statuses:
                errors.append(f"{rid}: source_url not in fetch log")
            elif "ok" not in statuses:
                errors.append(f"{rid}: source_url logged but not ok ({statuses})")
    return errors, warnings



def sources_root():
    """官方原文快照目录：新包在 rules/sources/，旧布局在 sources/。"""
    for cand in (os.path.join(BASE, "rules", "sources"), os.path.join(BASE, "sources")):
        if os.path.isdir(cand):
            return cand
    return os.path.join(BASE, "rules", "sources")

def main():
    import glob
    targets = sys.argv[1:] or sorted(glob.glob(os.path.join(BASE, "rules", "*_rules.json")))
    srcmap = build_source_map()
    log = load_log()
    total_err = total_warn = 0
    for t in targets:
        errs, warns = validate(t, srcmap, log)
        total_err += len(errs)
        total_warn += len(warns)
        name = os.path.basename(t)
        try:
            n = len(json.load(open(t, encoding="utf-8")).get("rules", []))
        except Exception:
            n = 0
        print(f"== {name}: {n} rules, {len(errs)} errors, {len(warns)} warnings")
        for e in errs:
            print("   FAIL", e)
        for w in warns:
            print("   warn", w)
    print()
    print("RESULT:", "ok" if total_err == 0 else "FAIL",
          f"({total_err} errors, {total_warn} warnings)")
    sys.exit(0 if total_err == 0 else 1)


if __name__ == "__main__":
    main()
