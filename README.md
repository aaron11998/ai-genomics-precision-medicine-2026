# The State of AI in Genomics & Precision Medicine — 2026

[![License: MIT](https://img.shields.io/badge/Code-MIT-yellow.svg)](LICENSE)
[![Data: CC0](https://img.shields.io/badge/Data-CC0--1.0-blue.svg)](DATA_LICENSE)
[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey.svg)](CITATION.cff)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Registry](https://img.shields.io/badge/Source-OpenAlex%20(CC0)-00695c.svg)](https://openalex.org)
[![Companion](https://img.shields.io/badge/Companion-ai--clinical--trials--2026-6a1b9a.svg)](https://github.com/aaron11998/ai-clinical-trials-2026)

**K-Dense Science Lab — Market Analysis Division**
*Snapshot: 2026-09-26T18:29:26Z · Source: OpenAlex · Works retrieved: 19,600 · Analyzed: 19,532 · Fresh server-side trend through 2026 YTD*

A reproducible market analysis of the OpenAlex cohort of works whose title or abstract
references AI/ML/DL **and** genomics/genome/precision medicine — 19,600 works retrieved,
19,532 analyzed, with a hybrid data basis (snapshot cohort through 2023 + fresh
server-side strict-pairing trend through 2026 YTD, both disclosed). Ships with the raw
extract, a flattened CSV, computed statistics, a zero-dependency Python pipeline, and
four publication-grade figures.

## Headline findings

1. **Exponential middle, not beginning.** Cohort works grew 155 (2010) → 3,910 (2022); the strict "machine learning"+"genomics" pairing shows the re-steepening: **2,149 (2024) → 3,570 (2025) → 4,155 by late Sep 2026**, +16.4% above all of 2025 with a quarter of the year left.
2. **US-centered at 2.8× China.** US 7,275 · China 2,556 · UK 1,552 · Germany 1,154 · India 1,045 (works to 2023).
3. **Universities publish, companies convert.** Harvard (479), Stanford (359), Penn (237), Cornell (234), Toronto (205) — no company in the top 10.
4. **Real impact, long tail.** Median 4 cites, mean 37.9, 6.8% of works ≥100 cites, mean FWCI 3.53; 68.8% open access.
5. **Applied oncogenomics is the center.** Top topics: gene expression and cancer classification (831), ML in bioinformatics (826), phylogenetics (784), cancer genomics and diagnostics (735).

Full narrative, methodology, caveats, and market implications: [`report/README.md`](report/README.md).

## Quickstart

```bash
git clone https://github.com/aaron11998/ai-genomics-precision-medicine-2026.git
cd ai-genomics-precision-medicine-2026

# Recompute all statistics from the shipped snapshot (stdlib only):
python3 code/recompute_stats.py   # → data/stats.json (from local snapshot)

# Or refresh everything from the live OpenAlex API (when the search cluster is healthy):
python3 code/fetch_build.py       # → data/genomics_ai_raw.jsonl + .csv + stats.json (~10 min)

# Rebuild the four figures (needs matplotlib):
pip install matplotlib
python3 code/make_figures.py      # → figures/fig1..fig4 (.png 300dpi + .pdf)

# Independent QA pass (stdlib only, exits 0 on green):
python3 code/qa_check.py
```

## Repository layout

| Path | Contents |
|---|---|
| `code/fetch_build.py` | Live pipeline: cursor-paginated OpenAlex pull, flatten to CSV, compute stats (stdlib only) |
| `code/recompute_stats.py` | Offline stats recompute from the shipped snapshot (stdlib only) |
| `code/make_figures.py` | Four publication-grade figures (Okabe-Ito palette, PNG 300 dpi + vector PDF) |
| `code/qa_check.py` | Independent verification: recomputes headline stats from the CSV, cross-checks vs `stats.json` |
| `data/genomics_ai_raw.jsonl` | 19,600 curated raw OpenAlex records (13 MB) |
| `data/genomics_ai_flat.csv` | Flattened table: 19,600 rows × 17 fields |
| `data/stats.json` | All computed statistics, machine-readable |
| `data/server_counts.json` | Fresh server-side strict-pairing trend counts (2024/2025/2026 YTD) + provenance notes |
| `figures/` | fig1 surge trend · fig2 era + document types · fig3 top countries · fig4 top institutions (PNG + PDF) |
| `report/README.md` | Full market report: methodology, findings, caveats, market implications |

## Dataset dictionary — `data/genomics_ai_flat.csv`

One row per OpenAlex work.

| # | Column | Type | Description |
|---|---|---|---|
| 1 | `openalex_id` | string | OpenAlex work ID (primary key, `W`-prefixed) |
| 2 | `doi` | string | DOI (empty if none) |
| 3 | `title` | string | Work display title |
| 4 | `publication_year` | int | Publication year |
| 5 | `publication_date` | ISO date | Full publication date |
| 6 | `work_type` | enum | OpenAlex type (`article`, `preprint`, `review-article`, …) |
| 7 | `is_retracted` | bool | OpenAlex retraction flag |
| 8 | `is_paratext` | bool | Paratext flag (front-matter; excluded from the analysis cohort) |
| 9 | `cited_by_count` | int | Raw citation count |
| 10 | `fwci` | float | Field-weighted citation impact (67.7% coverage) |
| 11 | `oa_is_oa` | bool | Open access flag |
| 12 | `oa_status` | enum | OA status (`gold`, `green`, `hybrid`, `closed`, …) |
| 13 | `journal` | string | Primary source/journal display name |
| 14 | `primary_topic` | string | OpenAlex primary topic |
| 15 | `primary_field` | string | OpenAlex primary field |
| 16 | `n_authors` | int | Authorship count |
| 17 | `institutions` | string | Author institution names, `\|`-separated (≤25) |
| 18 | `countries` | string | Author country codes, `\|`-separated (≤25) |

## Methodology (short form)

- **Source.** OpenAlex — open, CC0 scholarly metadata catalog.
- **Cohort query.** `("artificial intelligence" OR "machine learning" OR "deep learning") AND ("genomics" OR "genome" OR "precision medicine")` on title+abstract — a *lower bound*: works using AI without naming it are not captured.
- **Snapshot.** Cursor-paginated, select-pruned, 2026-09-26T18:29:26Z; 19,532 non-paratext works analyzed.
- **Hybrid trend.** 2024–2026 year counts from fresh server-side strict-pairing `"machine learning" AND "genomics"` meta.counts (2026 partial year); narrowness of that query disclosed — compare growth rates, not levels.
- **Verification.** Independent QA pass recomputes every headline statistic from the CSV; all checks green (see `code/qa_check.py`).
- **Caveats.** Keyword lower bound; affiliation fields present for a disclosed majority (>60% QA floor); country counts are work-level; FWCI coverage 67.7%; 33 retracted works counted and disclosed. Full list in [`report/README.md`](report/README.md) §2.

## Franchise companions

- Upstream→midstream: [The State of AI in Drug Discovery & Development — 2026](https://github.com/aaron11998/ai-drug-discovery-2026) (18,167 works)
- Midstream→downstream: [The State of AI in Clinical Trials — 2026](https://github.com/aaron11998/ai-clinical-trials-2026) (4,250 studies; 80 phased interventional)

## License & citation

- **Code** (`code/`): [MIT](LICENSE) — © 2026 K-Dense Science Lab.
- **Data** (`data/`): [CC0 1.0](DATA_LICENSE) — derived from OpenAlex (CC0); attribution appreciated: *"Source: OpenAlex, K-Dense analysis, Sep 2026."*
- **Figures / report text**: CC0 with attribution appreciated.

Cite via [CITATION.cff](CITATION.cff).

---
© 2026 K-Dense Science Lab · Market Analysis Division
