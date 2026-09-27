#!/usr/bin/env python3
"""
K-Dense Science Lab — QA pass for ai-genomics-precision-medicine-2026.
Independent verification: recomputes headline statistics directly from the
flattened CSV through a separate code path and cross-checks them against
data/stats.json (produced by code/fetch_build.py or code/recompute_stats.py
from the raw JSONL), plus the fresh server-side trend in
data/server_counts.json.

Cohort definition (mirrors the stats builders): statistics are computed on
non-paratext works (is_paratext == false).

Exit code 0 = all checks passed; nonzero = failure. Prints a per-check log.
"""
import csv, json, collections, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "data", "genomics_ai_flat.csv")
STATS_PATH = os.path.join(ROOT, "data", "stats.json")
RAW_PATH = os.path.join(ROOT, "data", "genomics_ai_raw.jsonl")
SRV_PATH = os.path.join(ROOT, "data", "server_counts.json")

failures = []
passed = 0


def check(name, ok, detail=""):
    global passed
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if ok:
        passed += 1
    else:
        failures.append(name)


def main():
    with open(STATS_PATH) as f:
        S = json.load(f)
    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    with open(RAW_PATH) as f:
        raw = [json.loads(line) for line in f]

    # --- Structural integrity -------------------------------------------------
    check("csv row count == raw jsonl line count",
          len(rows) == len(raw), f"{len(rows)} vs {len(raw)}")

    ids = [r["openalex_id"] for r in rows]
    check("unique openalex IDs in CSV (no duplicates)",
          len(ids) == len(set(ids)), f"{len(set(ids))} unique / {len(ids)}")

    check("meta.works_matched_union == csv rows",
          S["meta"]["works_matched_union"] == len(rows),
          f"{S['meta']['works_matched_union']} vs {len(rows)}")

    # Core fields must be near-complete; affiliation fields get a lower bar
    # (disclosed caveat: a minority of works lack institution/country metadata).
    core = ["openalex_id", "title", "publication_year", "work_type", "cited_by_count"]
    ok = all(sum(1 for r in rows if r[c].strip()) / len(rows) > 0.95 for c in core)
    check("core columns present for >95% of rows", ok,
          ", ".join(f"{c}:{100*sum(1 for r in rows if r[c].strip())/len(rows):.1f}%" for c in core))

    aff = ["countries", "institutions"]
    ok = all(sum(1 for r in rows if r[c].strip()) / len(rows) > 0.60 for c in aff)
    check("affiliation columns present for >60% of rows (caveat disclosed)", ok,
          ", ".join(f"{c}:{100*sum(1 for r in rows if r[c].strip())/len(rows):.1f}%" for c in aff))

    # --- Analysis cohort (non-paratext), recomputed from CSV -------------------
    cohort = [r for r in rows if r["is_paratext"].strip().lower() != "true"]
    check("cohort_non_paratext == rows minus paratext",
          S["meta"]["cohort_non_paratext"] == len(cohort),
          f"{len(cohort)} non-paratext of {len(rows)}")

    years = collections.Counter(r["publication_year"] for r in cohort
                                if r["publication_year"].strip())
    ok = all(years.get(y, 0) == v for y, v in S["works_by_year"].items()) and \
         sum(years.values()) == sum(S["works_by_year"].values())
    check("works_by_year recomputed from CSV (cohort) matches stats.json", ok,
          f"{len(years)} year buckets")

    # Snapshot is a works-through-2023 basis: the latest snapshot year must be
    # strictly below the first fresh server-side trend year.
    SRV = {}
    if os.path.exists(SRV_PATH):
        with open(SRV_PATH) as f:
            SRV = json.load(f)
    trend = SRV.get("strict_pairing_by_year") or {}
    if trend:
        last_snap = max(int(y) for y in years)
        first_trend = min(int(y) for y in trend)
        check("hybrid seam: snapshot ends before fresh trend begins",
              last_snap < first_trend,
              f"snapshot last year {last_snap} < trend first year {first_trend}")
        v24, v25, v26 = trend.get("2024"), trend.get("2025"), trend.get("2026")
        check("server trend monotone upward 2024->2025->2026YTD",
              v24 < v25 < v26,
              f"{v24} < {v25} < {v26}")
        check("2026 YTD exceeds full-year 2025 (headline claim)", v26 > v25,
              f"2026YTD={v26} vs 2025={v25} (+{100*(v26-v25)/v25:.1f}%)")
    else:
        check("server_counts.json present with strict_pairing_by_year", False,
              "fresh trend missing — headline claims unrecoverable")

    countries = collections.Counter(
        c for r in cohort for c in (x.strip() for x in r["countries"].split("|")) if c
    )
    ok = all(countries.get(k, 0) == v for k, v in S["top12_countries"].items())
    check("top12_countries recomputed from CSV matches stats.json", ok,
          f"top: {countries.most_common(3)}")

    insts = collections.Counter(
        i for r in cohort for i in (x.strip() for x in r["institutions"].split("|")) if i
    )
    ok = all(insts.get(k, 0) == v for k, v in S["top15_institutions"].items())
    check("top15_institutions recomputed from CSV matches stats.json", ok)

    cites = sorted(int(r["cited_by_count"]) for r in cohort)
    c = S["citations"]
    ok = (c["n"] == len(cites)
          and c["median"] == cites[len(cites) // 2]
          and c["p90"] == cites[int(0.9 * len(cites))])
    check("citation stats recomputed from CSV match stats.json", bool(ok),
          f"n={len(cites)}, median={cites[len(cites)//2]}, p90={cites[int(0.9*len(cites))]}")

    ge100 = sum(1 for x in cites if x >= 100)
    check("share_ge100_cites_pct matches CSV recompute",
          c["share_ge100_cites_pct"] == round(100 * ge100 / len(cites), 1),
          f"{ge100}/{len(cites)} = {c['share_ge100_cites_pct']}%")

    oa = sum(1 for r in cohort if r["oa_is_oa"].strip().lower() == "true")
    check("open_access_share_pct matches CSV recompute (cohort)",
          S["open_access_share_pct"] == round(100 * oa / len(cohort), 1),
          f"{oa}/{len(cohort)} = {S['open_access_share_pct']}%")

    retr = sum(1 for r in cohort if r["is_retracted"].strip().lower() == "true")
    check("retracted_count matches CSV recompute",
          S["retracted_count"] == retr, f"{retr} retracted works")

    # --- Plausibility probes ----------------------------------------------------
    n_topics = sum(S["top12_topics"].values())
    check("top12 topics hold a meaningful cohort share (10-60%)",
          10.0 <= 100 * n_topics / len(cohort) <= 60.0,
          f"{100 * n_topics / len(cohort):.1f}% of cohort in top 12 topics")

    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    ts = datetime.datetime.strptime(S["meta"]["fetched_at_utc"], "%Y-%m-%dT%H:%M:%SZ")
    check("snapshot timestamp parses and is <14 days old",
          now - ts < datetime.timedelta(days=14),
          S["meta"]["fetched_at_utc"])

    check("offline/served basis disclosed in stats meta",
          "unavailable_offline" in json.dumps(S["meta"]) or
          S["meta"].get("server_side_counts") is not None or
          "hybrid" in json.dumps(S["meta"]).lower(),
          "hybrid data basis must be disclosed, not hidden")

    # --- Verdict --------------------------------------------------------------
    total = passed + len(failures)
    print(f"\nQA verdict: {passed}/{total} checks passed")
    if failures:
        print("FAILED:", ", ".join(failures))
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
