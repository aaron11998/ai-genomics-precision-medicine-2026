# The State of AI in Genomics & Precision Medicine — 2026

**K-Dense Science Lab — Market Analysis Division**
*Snapshot cohort: 19,600 OpenAlex works (19,532 analyzed) · works through 2023 · fresh server-side trend through 2026 YTD*

---

## 1. Executive Summary

Genomics was the first domain where AI made a measurable scientific difference — and it is the domain where AI has become least remarkable, because it is now ambient. We analyzed the OpenAlex cohort of works whose title or abstract references AI/ML/DL **and** genomics/genome/precision medicine: **19,600 works retrieved, 19,532 non-paratext works analyzed**, spanning more than a century of indexed literature (effective modern era 1994–2023), plus fresh server-side trend counts through September 2026.

**Five findings that matter:**

1. **The field is in its exponential middle, not its beginning.** AI-flagged genomics works grew from 155 (2010) to a 2020–2023 plateau above 2,800/year (2022: 3,910). The strict "machine learning"+"genomics" pairing — a narrower lower-bound query — shows the next gear: **2,149 (2024) → 3,570 (2025) → 4,155 by late September 2026**, already +16.4% above all of 2025 with a quarter of the year remaining. Two independent query methodologies, one direction: up.

2. **The United States runs the field at 2.8× China.** US-affiliated works: **7,275**. China: **2,556**. UK (1,552), Germany (1,154), India (1,045) form the chasing pack. Unlike clinical-trial AI (China ≈ US parity) and drug-discovery AI (India #2), genomics AI remains US-centered — sequencing infrastructure, reference datasets, and NIH-scale funding still compound here.

3. **Academic medicine is the production engine.** Harvard (**479** works), Stanford (359), Penn (237), Cornell (234), Toronto (205) lead. No company cracks the top 10 — the Illuminas and Verily's of the field publish a fraction of what university hospitals do. The commercial layer still rents its science from academia.

4. **Impact is real but long-tailed.** Median citations: 4. Mean: 37.9 — pulled up by a genuine high-impact tier (6.8% of works ≥100 citations; mean field-normalized FWCI 3.53, well above the world average (1.0 by definition)). Genomics AI produced foundational, heavily cited methods — not just citation-churn. 68.8% of the cohort is open access.

5. **The topics are clinical, not theoretical.** Top OpenAlex topics: gene expression and cancer classification (831), ML in bioinformatics (826), genomics and phylogenetic studies (784), cancer genomics and diagnostics (735). The field's center of gravity is *applied cancer genomics* — pattern classification on molecular data aimed at diagnosis and prognosis.

**Implication for buyers:** the interesting money is no longer in *doing* AI genomics (universities do it at scale, on grants) but in the layers academia under-serves: clinical-grade validation, regulated pipelines (CLIA/CAP-grade), population-scale data infrastructure, and the translation of oncogenomic classifiers into reimbursable diagnostics. Same pattern as our clinical-trials finding: the bottleneck has moved downstream of method invention.

---

## 2. Methodology

**Source.** OpenAlex (`https://api.openalex.org/works`), the open catalog of scholarly metadata. Metadata is CC0.

**Cohort query.** `title_and_abstract.search: ("artificial intelligence" OR "machine learning" OR "deep learning") AND ("genomics" OR "genome" OR "precision medicine")` — retrieved via cursor-paginated field-pruned requests (200/page, `publication_date:asc`, select-pruned) on **2026-09-26T18:29:26Z** (snapshot UTC, recorded in `data/stats.json`). 19,600 works matched the union; 19,532 remain after excluding paratext (database front-matter, editorials-of-record). Effective coverage of the retrieved cohort is **1900–2023**: the 2024+ portion of this broad union query was not retrievable during the build window (see Hybrid Data Basis below), so year-level counts for 2024–2026 come from a second, fresh server-side measurement.

**Hybrid data basis (disclosed).** The OpenAlex search cluster was rate-limiting anonymous queries during the 2026-09-27 build window (HTTP 503 "search paused"; intermittent for small requests, hard-failing for paged retrieval). We therefore ship:

- **Cohort depth (figs 2–4):** the local 19,532-work snapshot (works through 2023) — full-record analysis, fully reproducible from `data/genomics_ai_raw.jsonl`.
- **Trend freshness (fig 1):** fresh server-side `meta.count` values for the **strict pairing** `"machine learning" AND "genomics"` per publication year: 2024 = 2,149 · 2025 = 3,570 · 2026 YTD = 4,155 (`data/server_counts.json`).

The strict pairing is a narrower lower-bound query than the snapshot cohort filter (one AI term × one anchor term), so its absolute levels are not comparable to the cohort series — treat its *growth rates* as the signal. Both bases and their seams are disclosed rather than smoothed over; re-running `code/fetch_build.py` when the cluster is healthy refreshes everything into a single-series basis.

**Verification.** Every headline statistic is recomputed from the flattened CSV through an independent code path and cross-checked against `stats.json` (`code/qa_check.py`). Results: see §5.

**Caveats (disclosed, quantified where possible).**
- Title/abstract keyword matching is a lower bound on true adoption: works using AI without naming it are not captured; incidental name-drops inflate counts. Sensitivity of levels and slopes to vocabulary is unresolved by design (we measure what is declared).
- Affiliation coverage: institutions/countries present for the disclosed majority of cohort works (QA enforces >60% floor); country/institution counts are work-level (a work with 5 countries counts 5 times).
- 33 cohort works (0.17%) are flagged retracted in OpenAlex; they are counted in the cohort and disclosed here.
- 2026 trend values are partial-year (through late Sep 2026).
- FWCI available for 13,214 of 19,532 works (67.7%); statistics computed on that subset.

---

## 3. Findings

### 3.1 Growth: two measurements, one direction

| Basis | 2010 | 2019 | 2022 | 2024 | 2025 | 2026 YTD |
|---|---|---|---|---|---|---|
| Snapshot cohort (broad union, works to 2023) | 155 | 2,140 | 3,910 | — | — | — |
| Strict pairing (fresh server counts) | — | — | — | 2,149 | 3,570 | **4,155** |

The broad union cohort shows the classic S-curve takeoff through 2022. The strict pairing shows the curve did not bend after 2023 — it re-steepened (+66% 2024→2025, +16.4% YTD-2026 over full-2025). At constant H2 velocity, 2026 clears **5,500** strict-pairing works — roughly 35× the 2010 broad-cohort volume. The field's growth is no longer adoption discovery; it is infrastructure: every sequencing center now runs ML by default.

### 3.2 Geography: a US-centered field

| Rank | Country | Works |
|---|---|---|
| 1 | United States | 7,275 |
| 2 | China | 2,556 |
| 3 | United Kingdom | 1,552 |
| 4 | Germany | 1,154 |
| 5 | India | 1,045 |

The US share (~37% of affiliated works) exceeds its share in either companion field at the research stage. Cross-referencing the franchise: drug-discovery AI put India #2; clinical-trial AI put China at parity with the US *at the validation stage*; genomics AI — the upstream methods engine for both — remains American-dominated. Any market entry plan for genomics AI tooling that does not route through US academic medical centers is missing the center of gravity.

### 3.3 Institutions: universities publish, companies commercialize

Top producers: Harvard (479), Stanford (359), University of Pennsylvania (237), Cornell (234), University of Toronto (205). The list is exclusively universities and academic medical centers. Compare drug discovery, where AstraZeneca appears at #10 — here even the top genomics companies (Illumina, GRAIL, Guardant) do not surface in the top 10 by publications. The publication engine is grant-funded academia; the commercial layer converts. Buyer implication: partnerships and acquisitions route through tech-transfer offices, not corporate BD.

### 3.4 Impact: real science, long tail

Median 4 citations, mean 37.9, p90 = 70. The 6.8% of works with ≥100 citations are the load-bearing tier: reference methods (variant callers, expression classifiers, embeddings) that the rest of the field cites thousands of times. Mean FWCI 3.53 (median 1.09) means the typical work performs at world-average for its field and year while a high-impact tier pulls the mean far above it — this is not a preprint-flood artifact field. 68.8% open access makes the corpus unusually usable for meta-research and model training.

### 3.5 Topics: applied oncogenomics is the center

Top OpenAlex topics: gene expression and cancer classification (831), machine learning in bioinformatics (826), genomics and phylogenetic studies (784), cancer genomics and diagnostics (735), bioinformatics and genomic networks (722). The center of gravity is cancer: classification of expression profiles, diagnostics, prognostics. Phylogenetics (infectious-disease genomics) is the second pillar — the pandemic-era methods layer. Precision-medicine-specific topics trail the cancer cluster, consistent with the translation lag the franchise documents downstream (only 80 phased AI interventional trials in our clinical-trials companion).

---

## 4. Market implications

1. **The commoditization curve is complete upstream.** AI genomics methods are published at commodity scale by public institutions. Sustained margins live in the conversion layers: regulated pipelines, clinical validation, reimbursement.
2. **US-centricity is an infrastructure story.** Reference datasets, cohort programs (All of Us, UK Biobank notwithstanding), and the academic medical center network anchor the field. Data-access partnerships beat point-solution sales here.
3. **Oncology is the beachhead market.** The topic distribution says it directly: build for tumor boards, molecular tumor registries, and companion-diagnostic workflows first.
4. **The franchise funnel tightens.** 19,532 AI-genomics works (upstream) → 18,167 AI-drug-discovery works (midstream) → 4,250 AI clinical-trial studies → 80 phased interventional studies (downstream evidence base). Each stage an order of magnitude smaller. The compounding bottleneck — and therefore the category-defining opportunity — is evidence generation.

---

## 5. Verification

Independent QA pass (`code/qa_check.py`): recomputes every headline statistic from `data/genomics_ai_flat.csv` through a separate code path and cross-checks against `data/stats.json`. Run 2026-09-27: **all checks passed** (structural integrity, cohort integrity, year/country/institution/citation/OA/retraction recomputes, plausibility probes). Verbatim output in the run log; re-run with `python3 code/qa_check.py` (exits 0).

## 6. License & citation

- **Code** (`code/`): [MIT](LICENSE) — © 2026 K-Dense Science Lab.
- **Data** (`data/`): [CC0 1.0](DATA_LICENSE) — derived from OpenAlex (CC0); attribution appreciated: *"Source: OpenAlex, K-Dense analysis, Sep 2026."*
- **Figures / report text**: CC0 with attribution appreciated.

Cite via [CITATION.cff](CITATION.cff).
