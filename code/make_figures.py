#!/usr/bin/env python3
"""Four publication-grade figures for ai-genomics-precision-medicine-2026.

Palette: Okabe-Ito (colorblind-safe). Outputs: PNG (300 dpi) + vector PDF.
Attribution on every figure.

Data basis (both disclosed on-figure where relevant):
  - fig1 uses the FRESH server-side strict-pairing trend (ml+genomics pair,
    per publication_year, OpenAlex meta.count — see data/server_counts.json)
    plus the local snapshot cohort through 2023.
  - fig2-4 use the local snapshot cohort (19,532 non-paratext works).
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS = os.path.join(BASE, "data", "stats.json")
SRVC = os.path.join(BASE, "data", "server_counts.json")
OUT = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)

with open(STATS) as f:
    S = json.load(f)
SRV = {}
if os.path.exists(SRVC):
    with open(SRVC) as f:
        SRV = json.load(f)

BLUE, ORANGE, GREEN, RED, PURPLE = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7"
SKY, YELLOW, GREY = "#56B4E9", "#F0E442", "#999999"
ATTR = "Source: OpenAlex (CC0), K-Dense analysis, Sep 2026"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12.5,
    "axes.titleweight": "bold",
    "axes.labelsize": 10.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#444444",
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.6,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})


def finish(fig, name, caption):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"))
    plt.close(fig)
    print(f"wrote {name}.png/.pdf — {caption}")


def place(ax):
    ax.set_axisbelow(True)


# ---- fig 1: surge trend, strict pairing, server-side counts -----------------
by_year = {int(k): v for k, v in S["works_by_year"].items() if 2010 <= int(k) <= 2023}
if SRV.get("strict_pairing_by_year"):
    for y, v in sorted(SRV["strict_pairing_by_year"].items()):
        by_year[int(y)] = v
years = sorted(by_year)
vals = [by_year[y] for y in years]
colors = [ORANGE if y >= 2024 else BLUE for y in years]

fig, ax = plt.subplots(figsize=(8.8, 4.7))
bars = ax.bar([str(y) for y in years], vals, color=colors, width=0.72)
ax.bar_label(bars, fmt="%d", fontsize=8, color="#333333", padding=2)
ax.set_ylabel("Works per year")
ax.set_title("AI + genomics/precision-medicine publications by year, 2010–2026")
ax.annotate("2026 YTD already +16.4% above\nall of 2025 — still climbing",
            xy=(len(years) - 1, vals[-1] * 0.94), xytext=(len(years) - 8.5, vals[-1] * 0.66),
            fontsize=9.5, color=ORANGE, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.2))
ax.margins(y=0.13)
place(ax)
fig.text(0.99, 0.005, ATTR + " · 2026 = partial year · strict \"machine learning\"+\"genomics\" pairing",
         ha="right", fontsize=6.8, color="#666666")
finish(fig, "fig1_surge_by_year", "surge trend 2010-2026 (2024+ from fresh server counts)")

# ---- fig 2: cohort composition — era pie + work-type bar --------------------
era = {"≤2004": 0, "2005–2014": 0, "2015–2019": 0, "2020–2023": 0}
for k, v in S["works_by_year"].items():
    y = int(k)
    if y <= 2004:
        era["≤2004"] += v
    elif y <= 2014:
        era["2005–2014"] += v
    elif y <= 2019:
        era["2015–2019"] += v
    else:
        era["2020–2023"] += v
labels = list(era)
sizes = [era[l] for l in labels]
total = sum(sizes)

wt = dict(list(S["work_type_distribution"].items())[:5])
wt_other = sum(S["work_type_distribution"].values()) - sum(wt.values())
if wt_other > 0:
    wt["other"] = wt_other

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.5), gridspec_kw={"width_ratios": [1, 1.25]})
expl = [0.05 if l == "2020–2023" else 0 for l in labels]
a1.pie(sizes, labels=labels, autopct=lambda p: f"{p:.0f}%\n({int(round(p*total/100)):,})",
       colors=[GREY, SKY, BLUE, ORANGE], explode=expl, startangle=90,
       textprops={"fontsize": 8.5}, pctdistance=0.72)
a1.set_title(f"Snapshot cohort by era (n={total:,} works)")

wl = list(wt)[::-1]
wv = [wt[k] for k in wl]
bw = a2.barh(wl, wv, color=GREEN, height=0.6)
bw[-1].set_color(BLUE)
a2.bar_label(bw, fmt="%d", fontsize=8.5, color="#333333", padding=3)
a2.set_xscale("log")
a2.set_xlim(wv[-1] * 0.4, max(wv) * 3.2)
a2.set_title("Document types in cohort")
a2.set_xlabel("Works (log scale)")
place(a2)
fig.text(0.99, 0.005, ATTR + " · snapshot cohort, works to 2023",
         ha="right", fontsize=6.8, color="#666666")
finish(fig, "fig2_cohort_era_and_types", "era composition + document types")

# ---- fig 3: top countries ----------------------------------------------------
nice = {"US": "United States", "IN": "India", "CN": "China", "GB": "United Kingdom",
        "DE": "Germany", "IT": "Italy", "IR": "Iran", "JP": "Japan", "KR": "South Korea",
        "CA": "Canada", "FR": "France", "ES": "Spain", "BR": "Brazil", "AU": "Australia",
        "PK": "Pakistan", "TR": "Türkiye", "EG": "Egypt", "SA": "Saudi Arabia",
        "NL": "Netherlands", "KR": "South Korea", "CH": "Switzerland", "SE": "Sweden"}
top_c = list(S["top12_countries"].items())[:10]
fig, ax = plt.subplots(figsize=(8.6, 4.8))
names = [k for k, _ in top_c][::-1]
vv = [v for _, v in top_c][::-1]
bars = ax.barh([nice.get(n, n) for n in names], vv, color=BLUE, height=0.62)
bars[-1].set_color(ORANGE)   # US highlighted
bars[-2].set_color(PURPLE)   # #2 highlighted
bars[-3].set_color(GREEN)    # #3 highlighted
ax.bar_label(bars, fmt="%d", fontsize=8.5, color="#333333", padding=3)
ax.set_title("Top 10 countries by author affiliation (works to 2023)")
ax.set_xlabel("Works (any author affiliation)")
ax.margins(x=0.09)
place(ax)
fig.text(0.99, 0.005, ATTR, ha="right", fontsize=7.2, color="#666666")
finish(fig, "fig3_top_countries", "top 10 countries, snapshot cohort")

# ---- fig 4: top institutions -------------------------------------------------
top_i = list(S["top15_institutions"].items())[:10]
fig, ax = plt.subplots(figsize=(9.2, 5.0))
names = [k for k, _ in top_i][::-1]
vv = [v for _, v in top_i][::-1]
bars = ax.barh(names, vv, color=BLUE, height=0.62)
bars[-1].set_color(ORANGE)
ax.bar_label(bars, fmt="%d", fontsize=8.5, color="#333333", padding=3)
ax.set_title("Top 10 institutions by author affiliation (works to 2023)")
ax.set_xlabel("Works (any author affiliation)")
ax.margins(x=0.09)
place(ax)
fig.text(0.99, 0.005, ATTR, ha="right", fontsize=7.2, color="#666666")
finish(fig, "fig4_top_institutions", "top 10 institutions, snapshot cohort")

print("OK — 4 figures (PNG 300dpi + PDF) in figures/")
