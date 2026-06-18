# Live Seller Churn Analysis

Interactive dashboard and data pipeline for analyzing **eBay Live seller churn** in 2026. Sellers are grouped into **weekly cohorts** based on when they first streamed on Live, then measured for retention and churn at fixed tenure milestones.

**Primary dashboard:** `live_seller_churn_dashboard_20260618.html`  
**GitHub:** [devkashikar/live-seller-churn-analysis](https://github.com/devkashikar/live-seller-churn-analysis)

---

## Table of contents

1. [What this project does](#what-this-project-does)
2. [Repository structure](#repository-structure)
3. [Data files and paths](#data-files-and-paths)
4. [Seller population and cohorts](#seller-population-and-cohorts)
5. [Retail weeks and tenure](#retail-weeks-and-tenure)
6. [How churn is calculated](#how-churn-is-calculated)
7. [Dashboard components](#dashboard-components)
8. [Filters and edge cases](#filters-and-edge-cases)
9. [Build and refresh workflow](#build-and-refresh-workflow)
10. [Where calculations live (Python vs JavaScript)](#where-calculations-live-python-vs-javascript)
11. [Validation helpers](#validation-helpers)

---

## What this project does

This analysis answers:

- How many sellers **first streamed on eBay Live in 2026**, by retail week cohort?
- At key tenure points (roughly **1 month**, **2.5 months**, **4 months** after first stream), what share have **not streamed** in a defined window?
- How does **3-week rolling churn** evolve week-by-week within each cohort (heatmap table)?

The dashboard is a **standalone HTML file** with embedded JSON data. Open it in any browser — no server required. Filters (country, sub category) recompute metrics in the browser.

---

## Repository structure

```
live-seller-churn-analysis/
├── README.md                              # This file
├── streams_first_stream_2026.csv          # Source: all Live streams for 2026 first-time sellers
├── _build_canvas.py                       # CSV → compact JSON for the dashboard
├── _canvas_data.json                      # Intermediate / standalone JSON dataset
├── live_seller_churn_dashboard_20260618.html  # Current dashboard (embedded data + UI)
├── live_seller_churn_dashboard_20260617.html  # Earlier dashboard version
├── _build_html.py                         # Legacy HTML builder (older retention view)
├── _check.js                              # JS harness mirroring dashboard logic
├── _harness.js                            # Quick compute() smoke test
└── .gitignore
```

---

## Data files and paths

### Source data

| Path | Description |
|------|-------------|
| `streams_first_stream_2026.csv` | **Primary source file.** One row per **live stream event** for sellers whose first Live stream occurred in 2026. |

**Key columns used in this project:**

| Column | Role |
|--------|------|
| `SLR_ID` | Seller identifier — used to group streams per seller |
| `ID` | Stream / event identifier (one row = one stream, not one seller) |
| `STRT_TM` | Stream start timestamp |
| `RETAIL_WEEK` | 2026 retail week number for **this stream row** (Sun–Sat calendar) |
| `first_stream_dt` | Seller’s first-ever Live stream date (consistent across rows for that seller) |
| `SELLER_COUNTRY` | Seller country |
| `FCSD_VRTCL_SUP_GRP_revised` | Sub category (vertical) used in filters |
| `Seller_Tier_Tranche`, `Org` | Present in source; not used in current dashboard filters |

Rows with `RETAIL_WEEK = 53` are excluded during the build step.

### Processed data

| Path | Description |
|------|-------------|
| `_canvas_data.json` | Compact JSON produced by `_build_canvas.py`. Lists sellers with country/tier/org indices and all `(retail_week, vertical)` stream pairs. |
| Embedded `DATA` object in `live_seller_churn_dashboard_20260618.html` | Same structure as `_canvas_data.json`, inlined in the HTML for portability. |

### Dashboard

| Path | Description |
|------|-------------|
| `live_seller_churn_dashboard_20260618.html` | **Use this file.** Latest UI: summary cards, heatmap, cohort line chart, country + sub category filters. |

---

## Seller population and cohorts

### Who is in the analysis?

- Sellers who **first streamed on eBay Live in 2026** (per `first_stream_dt` / earliest stream in the extract).
- Current embedded dataset: **~2,570 sellers** with stream activity through **retail week 24** (as of the June 2026 data cut).
- Countries in data: UK, IT, US, DE, FR, AU, CA, Other Countries (Other Countries is **hidden from the filter dropdown** but included when no country filter is applied).

### Cohort definition

A **cohort** is the **2026 retail week of a seller’s first Live stream**.

**Rules:**

1. Each seller belongs to **exactly one cohort** — the retail week of their earliest stream.
2. Cohort label format: `26RW01`, `26RW02`, … `26RW24` (2026 retail week 1–24).
3. All sellers in a cohort row share the same **first-stream retail week**, but may have different countries, categories, and later streaming patterns.

### How cohort is assigned in code

**Python (`_build_canvas.py`):** For each `SLR_ID`, collect all `RETAIL_WEEK` values from stream rows. Cohort = `min(weeks)`.

**JavaScript (`compute()` in HTML):** After filters, cohort = minimum retail week in the seller’s filtered week set.

This matches mapping `STRT_TM` / `first_stream_dt` to a retail week because `RETAIL_WEEK` on each row is already aligned to the stream date.

### Excluded cohorts

Cohorts **26RW21–26RW24** are **hidden** from the dashboard (`EXCLUDED_COHORTS = {21, 22, 23, 24}`). Those sellers have not been on Live long enough for fair comparison at later tenure milestones (e.g. W16).

---

## Retail weeks and tenure

### 2026 retail week calendar

Retail weeks run **Sunday–Saturday**. Week 1 of 2026 starts **Jan 4, 2026**.

| Retail week | Date range (2026) |
|-------------|-------------------|
| 26RW01 | Jan 4 – Jan 10 |
| 26RW02 | Jan 11 – Jan 17 |
| 26RW03 | Jan 18 – Jan 24 |
| 26RW04 | Jan 25 – Jan 31 |
| … | … |
| 26RW24 | Jun 14 – Jun 20 |

(Full mapping is in `RW_DATES` inside the dashboard HTML.)

### Tenure weeks (W1, W4, W10, W16, …)

Tenure is measured in **weeks since the cohort’s first-stream retail week**, using **calendar retail weeks**:

- Cohort retail week = `c` (e.g. seller first streamed in 26RW05 → `c = 5`).
- **W1** = retail week `c + 1`
- **W2** = retail week `c + 2`
- **Wk** = retail week `c + k`

A seller is **retained** for a check window if they have **at least one stream** in any week inside that window. They are **churned** if they have **no stream** in any week of the window.

**Tenure milestones used in summary cards:**

| Label | Measured at | Tenure (~) | Stream window checked |
|-------|-------------|------------|------------------------|
| **New seller churn** | W4 | ~1 month | No stream in W1, W2, W3 |
| **Growing seller churn** | W10 | ~2.5 months | No stream in W7, W8, W9 |
| **Mature seller churn** | W16 | ~4 months | No stream in W13, W14, W15 |

These are **lifecycle checkpoints**, not permanent seller segments. The same seller is evaluated at W4, W10, and W16 with different windows.

---

## How churn is calculated

All churn metrics are computed in **`compute()`** inside `live_seller_churn_dashboard_20260618.html` (JavaScript). Python only prepares the seller/week dataset.

### Per-cohort churn rate

For a cohort of size `N` at a measurement point:

```
churn_rate = churned_count / N
churned_count = N - retained_count
retained_count = sellers with ≥1 stream in the defined week window
```

### Summary card weighted averages

Summary cards do **not** average cohort percentages. They use a **weighted average**:

```
weighted_churn% = sum(churned across eligible cohorts) / sum(starters across eligible cohorts) × 100
```

A cohort is **eligible** only if enough calendar time has passed:

| Metric | Eligibility rule |
|--------|------------------|
| New seller (W4) | `maxWeek - cohort >= 4` |
| Growing seller (W10) | `maxWeek - cohort >= 10` |
| Mature seller (W16) | `maxWeek - cohort >= 16` |

`maxWeek` is the latest retail week observed in the filtered data (currently week 24).

**Example (unfiltered, approximate):**

| Metric | Rate | Churned / Starters |
|--------|------|-------------------|
| New seller | ~17.9% | 370 / 2,062 |
| Growing seller | ~32.4% | 396 / 1,221 |
| Mature seller | ~34.1% | 120 / 352 |

Mature seller denominators are smaller because only cohorts 1–8 have ≥16 weeks of follow-up with data through week 24.

### Heatmap table: 3-week gap churn

The table shows **rolling 3-week churn** from **W4 onward** (columns W4, W5, W6, …).

For column **Wk** (where `k ≥ 4`):

- Look back at weeks **W(k−3), W(k−2), W(k−1)** relative to tenure (retail weeks `c+k−3`, `c+k−2`, `c+k−1`).
- **Churned** if the seller had **no stream** in any of those three weeks.
- **Retained** if they streamed in **at least one** of those three weeks.

Examples:

| Column | Window checked (tenure weeks) |
|--------|-------------------------------|
| W4 | W1, W2, W3 |
| W5 | W2, W3, W4 |
| W10 | W7, W8, W9 |
| W23 | W20, W21, W22 |

**Note:** Summary card “new seller churn” at W4 uses the **same window as W4 in the table** (W1–W3). Summary cards at W10 and W16 use **fixed windows** (W7–W9 and W13–W15), which differ from the table’s rolling definition at those columns.

Cell display:

- **Churn %** (default): `churned / cohort_size × 100`
- **Counts**: raw number of churned sellers

Heatmap color scales by churn (green = low, red = high), compressed so ~0–60% churn uses the full color range.

### Cohort line chart

Below the table, a line chart plots **per-cohort churn %** (not weighted) for:

- New seller (W4) — blue
- Growing seller (W10) — yellow
- Mature seller (W16) — red

Lines stop where cohorts lack enough follow-up (e.g. mature line only through cohorts that have reached W16).

---

## Dashboard components

### Summary cards (top)

1. **Total sellers** — count of sellers across all cohort rows after filters.
2. **New seller churn (at W4)** — weighted %; no stream in W1–W3.
3. **Growing seller churn (at W10)** — weighted %; no stream in W7–W9.
4. **Mature seller churn (at W16)** — weighted %; no stream in W13–W15.

### Filters

- **Seller Country** — multi-select; empty selection = all countries.
- **Sub category** — multi-select on `FCSD_VRTCL_SUP_GRP_revised`; empty = all categories.

### Heatmap table

- Rows: cohort week (26RWxx with date range).
- Column **Sellers First Streamed on Live**: cohort size.
- Columns W4+: 3-week gap churn.

### Line chart

- X-axis: **Cohort week (2026)**
- Y-axis: Churn rate (%)
- Three tenure lines as above.

---

## Filters and edge cases

### Country filter

Filters sellers by `SELLER_COUNTRY`. Seller is excluded entirely if country does not match.

### Sub category filter

When sub category is selected, only stream rows matching that vertical contribute to the seller’s **week set**. This can:

- Remove weeks where the seller streamed in other categories.
- Change which weeks count toward retention/churn.
- In edge cases, change the inferred cohort (`min(weeks)`) if the seller’s first stream was in a different category.

### One seller, one cohort

Within a given filter state, each seller appears in **one cohort row only**.

### Comebacks

If a seller streams again after a gap, they are **not churned** for weeks where the look-back window includes that stream. Churn is a **point-in-time** snapshot per column, not permanent removal.

### Data recency

Metrics depend on `maxWeek` in the extract. Cohorts that have not aged enough are excluded from specific metrics (not from the cohort row itself unless in `EXCLUDED_COHORTS`).

---

## Build and refresh workflow

### Prerequisites

- Python 3.x (no third-party packages required for `_build_canvas.py`)

### Step 1: Build JSON from CSV

```bash
python _build_canvas.py
```

Reads `streams_first_stream_2026.csv`, writes `_canvas_data.json`, prints cohort sanity-check stats.

### Step 2: Update embedded dashboard data

The current dashboard embeds JSON directly in the HTML. After rebuilding `_canvas_data.json`, update the `const DATA = …` block in `live_seller_churn_dashboard_20260618.html` (or automate via a small script).

### Step 3: View dashboard

Open in a browser:

```bash
open live_seller_churn_dashboard_20260618.html
```

Or double-click the file locally. No build step is required for viewing if HTML already contains embedded data.

---

## Where calculations live (Python vs JavaScript)

| Step | File | What it does |
|------|------|--------------|
| Data ingest | `_build_canvas.py` | CSV → seller list with `(week, vertical)` pairs |
| **Churn math** | `live_seller_churn_dashboard_20260618.html` → `compute()` | All churn, retention, weighted averages, chart series |
| Legacy | `_build_html.py` | Older retention dashboard (different churn definition) |

**There is no Python churn calculation for the current dashboard.** `_build_canvas.py` only shapes data; `_build_html.py` targets an older HTML template.

---

## Validation helpers

| File | Purpose |
|------|---------|
| `_check.js` | Node script with mirrored `compute()` logic for regression checks |
| `_harness.js` | Minimal smoke test: runs `compute()` and prints cohort list |

Run (requires extracting or loading dashboard JS context):

```bash
node _harness.js
```

---

## Quick reference: churn definitions

```
NEW SELLER (W4):     churned if no stream in weeks c+1, c+2, c+3
GROWING (W10):       churned if no stream in weeks c+7, c+8, c+9
MATURE (W16):        churned if no stream in weeks c+13, c+14, c+15

TABLE at Wk (k≥4):   churned if no stream in weeks c+k-3, c+k-2, c+k-1

where c = cohort retail week (first stream week)
```

---

## Contact / maintenance

When refreshing data:

1. Replace or update `streams_first_stream_2026.csv`.
2. Run `python _build_canvas.py`.
3. Re-embed JSON into the latest HTML dashboard.
4. Verify summary card totals and cohort row counts against expectations.
5. Commit and push to this repository.

For questions about retail week definitions or upstream extract logic, refer to the eBay Live streams source that produces `streams_first_stream_2026.csv`.
