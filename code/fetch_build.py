#!/usr/bin/env python3
"""
K-Dense Science Lab — "The State of AI in Genomics & Precision Medicine — 2026"
Data pipeline: fetch the OpenAlex cohort of works whose title/abstract references
AI/ML/DL AND ("genomics" OR "genome" OR "precision medicine"), flatten to CSV,
compute descriptive market statistics to stats.json.

Zero-dependency (stdlib only). Reproducible: re-run to refresh with live data.
Query provenance:
  title_and_abstract.search: ("artificial intelligence" OR "machine learning"
  OR "deep learning") AND ("genomics" OR "genome" OR "precision medicine")
Data license: OpenAlex metadata is CC0. Snapshot UTC timestamp recorded in stats.
"""
import json, time, urllib.request, urllib.parse, csv, collections, statistics, sys, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
os.makedirs(DATA, exist_ok=True)

BASE = "https://api.openalex.org/works"
UA = {"User-Agent": "KDenseLab/1.0 (github.com/aaron11998)"}
# Optional SOCKS5 egress (e.g. codespace tunnel) when the shared-IP free budget
# is exhausted; urllib cannot do SOCKS natively — route via curl subprocess.
SOCKS = os.environ.get("OPENALEX_SOCKS", "")  # e.g. 127.0.0.1:1080
AI_TERMS = ["artificial intelligence", "machine learning", "deep learning"]
ANCHOR_TERMS = ["genomics", "genome", "precision medicine"]
# Valid select keys only (invalid keys silently disable select pruning).
SELECT = ("id,display_name,doi,publication_year,publication_date,type,"
          "cited_by_count,open_access,primary_location,primary_topic,"
          "authorships,is_retracted,is_paratext,fwci,"
          "countries_distinct_count,institutions_distinct_count")
PER_PAGE = 200
SNAPSHOT_CUTOFF = "2026-09-26"  # partial-year disclosure handled in stats/report


def cohort_filter():
    terms = " OR ".join(f'"{t}"' for t in AI_TERMS)
    anchors = " OR ".join(f'"{t}"' for t in ANCHOR_TERMS)
    # NOTE: single search value; grouping the whole expression works server-side
    # (nested parentheses inside two separate search clauses return 0/400).
    return f"title_and_abstract.search:({terms}) AND ({anchors})"


def fetch_json(url, tries=10):
    last = None
    for a in range(tries):
        try:
            if SOCKS:
                cmd = ["curl", "-s", "--max-time", "120",
                       "--socks5-hostname", SOCKS, "-A", UA["User-Agent"], url]
                r = subprocess.run(cmd, capture_output=True, timeout=150)
                if r.returncode != 0 or not r.stdout:
                    raise RuntimeError(f"curl rc={r.returncode}: {r.stderr[:120]}")
                return json.loads(r.stdout.decode("utf-8"))
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            # exponential backoff; extra wait on 429 rate limiting
            wait = 2 * (a + 1)
            if "429" in str(e):
                wait = 20 * (a + 1)
            print(f"  retry {a + 1}/{tries} after {wait}s ({e})", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"fetch failed after {tries}: {last} :: {url[:140]}")


def fetch_all():
    flt = cohort_filter()
    params = {
        "filter": flt,
        "per-page": str(PER_PAGE),
        "select": SELECT,
        "sort": "publication_date:asc",  # deterministic page order
    }
    works, cursor, total, pages = [], "*", None, 0
    while True:
        p = dict(params)
        p["cursor"] = cursor
        url = BASE + "?" + urllib.parse.urlencode(p)
        data = fetch_json(url)
        total = data.get("meta", {}).get("count", total)
        works.extend(data.get("results", []))
        pages += 1
        cursor = data.get("meta", {}).get("next_cursor")
        print(f"page {pages}: fetched {len(works)}/{total}", flush=True)
        if not cursor or pages > 400:
            break
        time.sleep(1.1)  # polite pool (429-safe; sustained paged reads)
    return works, total


def squash(w):
    """Curated field-pruned record (the archived 'raw' form)."""
    oa = w.get("open_access") or {}
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    topic = w.get("primary_topic") or {}
    field = topic.get("field") or {}
    auths = w.get("authorships") or []
    insts, countries = [], []
    for a in auths:
        for i in a.get("institutions") or []:
            nm = i.get("display_name")
            if nm and nm not in insts:
                insts.append(nm)
        for c in a.get("countries") or []:
            if c and c not in countries:
                countries.append(c)
    return {
        "openalex_id": (w.get("id") or "").rsplit("/", 1)[-1],
        "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
        "title": w.get("display_name"),
        "publication_year": w.get("publication_year"),
        "publication_date": w.get("publication_date"),
        "work_type": w.get("type"),
        "is_retracted": bool(w.get("is_retracted")),
        "is_paratext": bool(w.get("is_paratext")),
        "cited_by_count": w.get("cited_by_count", 0),
        "fwci": w.get("fwci"),
        "oa_is_oa": bool(oa.get("is_oa")),
        "oa_status": oa.get("oa_status"),
        "journal": src.get("display_name"),
        "primary_topic": topic.get("display_name"),
        "primary_field": field.get("display_name"),
        "n_authors": len(auths),
        "institutions": insts[:25],
        "countries": countries[:25],
    }


def main():
    works, total = fetch_all()
    if not works:
        print("FATAL: empty cohort", flush=True)
        return 1

    squashed = [squash(w) for w in works]
    raw_path = os.path.join(DATA, "genomics_ai_raw.jsonl")
    with open(raw_path, "w") as f:
        for s in squashed:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    csv_path = os.path.join(DATA, "genomics_ai_flat.csv")
    cols = list(squashed[0].keys())
    with open(csv_path, "w", newline="") as f:
        wtr = csv.DictWriter(f, fieldnames=cols)
        wtr.writeheader()
        for s in squashed:
            row = dict(s)
            row["institutions"] = " | ".join(s["institutions"])
            row["countries"] = " | ".join(s["countries"])
            wtr.writerow(row)

    # Non-paratext research works form the analysis cohort
    cohort = [s for s in squashed if not s["is_paratext"]]

    def year_of(s):
        y = s["publication_year"]
        return str(y) if y else None

    by_year = collections.Counter(y for y in map(year_of, cohort) if y)
    wtype = collections.Counter(s["work_type"] or "UNKNOWN" for s in cohort)
    oa_status = collections.Counter(s["oa_status"] or "unknown" for s in cohort)
    journals = collections.Counter(
        s["journal"].strip() for s in cohort if s["journal"]
    )
    insts = collections.Counter(
        i.strip() for s in cohort for i in s["institutions"]
    )
    countries = collections.Counter(
        c for s in cohort for c in s["countries"]
    )
    topics = collections.Counter(
        s["primary_topic"] for s in cohort if s["primary_topic"]
    )
    fields = collections.Counter(
        s["primary_field"] for s in cohort if s["primary_field"]
    )
    cites = [s["cited_by_count"] for s in cohort
             if isinstance(s["cited_by_count"], int)]
    fwcis = [s["fwci"] for s in cohort if isinstance(s["fwci"], (int, float))]

    # Per-term server-side counts (work can match >1 term; sums exceed union)
    term_counts = {}
    for t in AI_TERMS + ANCHOR_TERMS:
        flt = (f'title_and_abstract.search:("{t}") AND ('
               + " OR ".join(f'"{a}"' for a in ANCHOR_TERMS) + ") AND ("
               + " OR ".join(f'"{a}"' for a in AI_TERMS) + ")")
        url = BASE + "?" + urllib.parse.urlencode({
            "filter": flt, "per-page": "1"})
        term_counts[t] = fetch_json(url)["meta"]["count"]
        time.sleep(0.35)
    # Anchor-only count for vertical context (broad genomics+PM literature)
    url = BASE + "?" + urllib.parse.urlencode({
        "filter": 'title_and_abstract.search:("genomics" OR "precision medicine" OR "personalized medicine")',
        "per-page": "1"})
    anchor_total = fetch_json(url)["meta"]["count"]

    cs = sorted(cites)
    stats = {
        "meta": {
            "source": "OpenAlex (api.openalex.org), snapshot of curated scholarly metadata",
            "data_license": "OpenAlex data is CC0 (https://openalex.org)",
            "query": {"title_and_abstract.search":
                      '(AI OR ML OR DL terms) AND ("genomics" OR "genome" OR "precision medicine")'},
            "ai_terms": AI_TERMS,
            "anchor_terms": ANCHOR_TERMS,
            "fetched_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "snapshot_cutoff": SNAPSHOT_CUTOFF,
            "works_matched_union": len(works),
            "cohort_non_paratext": len(cohort),
            "unique_openalex_ids": len({s['openalex_id'] for s in squashed}),
            "anchor_total_genomics_precision_works": anchor_total,
            "pipeline": "fetch_build.py (cursor pagination, per-page=200, "
                        "publication_date:asc, select-pruned)",
        },
        "works_by_year": dict(sorted(by_year.items())),
        "term_counts": term_counts,
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
    with open(os.path.join(DATA, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(json.dumps(stats["meta"], indent=2))
    print("works_by_year:", stats["works_by_year"])
    print("term_counts:", stats["term_counts"])
    print("top countries:", list(stats["top12_countries"].items())[:5])
    print("top institutions:", list(stats["top15_institutions"].items())[:5])
    print("top topics:", list(stats["top12_topics"].items())[:5])
    print("OK — wrote data/genomics_ai_raw.jsonl, genomics_ai_flat.csv, stats.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
