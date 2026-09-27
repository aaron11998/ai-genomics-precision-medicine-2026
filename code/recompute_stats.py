#!/usr/bin/env python3
"""
Recompute stats.json from the LOCAL snapshot (genomics_ai_raw.jsonl /
genomics_ai_flat.csv) when the OpenAlex search cluster is unavailable.
Produces the identical stats.json schema as fetch_build.py, except:
  - term_counts / anchor_total (server-side counts) are omitted and marked
    "unavailable_offline" — figures consuming them must degrade gracefully.
  - fetched_at_utc reflects the SNAPSHOT time (raw jsonl mtime, UTC).
Snapshot provenance: OpenAlex cursor-paginated pull, 2026-09-26 22:29 local.
"""
import json, csv, collections, statistics, sys, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "genomics_ai_raw.jsonl")
OUT = os.path.join(ROOT, "data", "stats.json")

with open(RAW) as f:
    squashed = [json.loads(line) for line in f]
if not squashed:
    print("FATAL: empty snapshot")
    sys.exit(1)

cohort = [s for s in squashed if not s["is_paratext"]]

def year_of(s):
    y = s.get("publication_year")
    return str(y) if y else None

by_year = collections.Counter(y for y in map(year_of, cohort) if y)
wtype = collections.Counter(s["work_type"] or "UNKNOWN" for s in cohort)
oa_status = collections.Counter(s["oa_status"] or "unknown" for s in cohort)
journals = collections.Counter(s["journal"].strip() for s in cohort if s["journal"])
insts = collections.Counter(i.strip() for s in cohort for i in s["institutions"])
countries = collections.Counter(c for s in cohort for c in s["countries"])
topics = collections.Counter(s["primary_topic"] for s in cohort if s["primary_topic"])
fields = collections.Counter(s["primary_field"] for s in cohort if s["primary_field"])
cites = [s["cited_by_count"] for s in cohort if isinstance(s["cited_by_count"], int)]
fwcis = [s["fwci"] for s in cohort if isinstance(s["fwci"], (int, float))]

mtime = os.path.getmtime(RAW)
fetched_at = datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

cs = sorted(cites)
stats = {
    "meta": {
        "source": "OpenAlex (api.openalex.org), snapshot of curated scholarly metadata",
        "data_license": "OpenAlex data is CC0 (https://openalex.org)",
        "query": {"title_and_abstract.search":
                  '(AI OR ML OR DL terms) AND ("genomics" OR "genome" OR "precision medicine")'},
        "ai_terms": ["artificial intelligence", "machine learning", "deep learning"],
        "anchor_terms": ["genomics", "genome", "precision medicine"],
        "fetched_at_utc": fetched_at,
        "snapshot_cutoff": fetched_at[:10],
        "works_matched_union": len(squashed),
        "cohort_non_paratext": len(cohort),
        "unique_openalex_ids": len({s["openalex_id"] for s in squashed}),
        "anchor_total_genomics_precision_works": None,
        "server_side_counts": "unavailable_offline: OpenAlex search cluster was rate-limiting anonymous queries at stats build time (2026-09-27); per-term and anchor counts omitted. Re-run code/fetch_build.py when the cluster recovers to refresh.",
        "pipeline": "recompute_stats.py from local snapshot (genomics_ai_raw.jsonl); original pull via fetch_build.py cursor pagination, per-page=200, publication_date:asc, select-pruned",
    },
    "works_by_year": dict(sorted(by_year.items())),
    "term_counts": {"unavailable_offline": True},
    "work_type_distribution": dict(wtype.most_common()),
    "oa_status_distribution": dict(oa_status.most_common()),
    "open_access_share_pct": round(100 * sum(1 for s in cohort if s["oa_is_oa"]) / len(cohort), 1),
    "top15_journals": dict(journals.most_common(15)),
    "top15_institutions": dict(insts.most_common(15)),
    "top12_countries": dict(countries.most_common(12)),
    "top12_topics": dict(topics.most_common(12)),
    "top8_fields": dict(fields.most_common(8)),
    "citations": {
        "n": len(cites),
        "median": int(statistics.median(cites)) if cites else None,
        "mean": round(statistics.mean(cites), 1) if cites else None,
        "p90": cs[int(0.9 * len(cs))] if cites else None,
        "share_ge100_cites_pct": round(100 * sum(1 for c in cites if c >= 100) / len(cites), 1) if cites else None,
    },
    "fwci": {
        "n_with_fwci": len(fwcis),
        "mean": round(statistics.mean(fwcis), 2) if fwcis else None,
        "median": round(statistics.median(fwcis), 2) if fwcis else None,
    },
    "retracted_count": sum(1 for s in cohort if s["is_retracted"]),
    "momentum": {
        "share_2024_to_2026YTD_pct": round(
            100 * sum(v for k, v in by_year.items() if k in ("2024", "2025", "2026")) / len(cohort), 1),
        "ytd_2026_note": "2026 is a partial year; compare YTD only",
    },
}
with open(OUT, "w") as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

print("cohort:", len(cohort), "of", len(squashed))
print("snapshot fetched_at_utc:", fetched_at)
print("works_by_year 2020+:", {k: v for k, v in stats["works_by_year"].items() if int(k) >= 2020})
print("top countries:", list(stats["top12_countries"].items())[:5])
print("top institutions:", list(stats["top15_institutions"].items())[:5])
print("top topics:", list(stats["top12_topics"].items())[:5])
print("citations:", stats["citations"])
print("fwci:", stats["fwci"])
print("oa share:", stats["open_access_share_pct"], "%  retracted:", stats["retracted_count"])
print("momentum:", stats["momentum"])
print("OK — wrote data/stats.json")
