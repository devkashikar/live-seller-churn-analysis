# Live Seller Churn Dashboard — Complete Guide

**Document version:** June 2026  
**Dashboard file:** `dashboard/live_seller_churn_dashboard_20260618.html`  
**Repository:** https://github.com/devkashikar/live-seller-churn-analysis

This guide explains every section of the churn dashboard, how metrics are calculated, which repository files are involved, and how to refresh or modify the analysis.

---

## 1. Purpose of the dashboard

The Live Seller Churn Dashboard tracks **eBay Live sellers who first streamed in 2026**. It measures whether sellers continue to go live over time and summarizes **churn** (sellers who stop streaming) at:

- **Early tenure** (~1 month) — new seller churn at W4  
- **Mid tenure** (~2.5 months) — growing seller churn at W10  
- **Later tenure** (~4 months) — mature seller churn at W16  

It also shows **rolling 3-week churn** in a cohort heatmap for every week from W4 onward.

The dashboard is a **single HTML file** that runs entirely in your browser. No server, database, or install is required.

---

## 2. How to open the dashboard

1. Clone or download this repository.  
2. Open **`dashboard/live_seller_churn_dashboard_20260618.html`** in Chrome, Edge, Firefox, or Safari.  
3. Use **Seller Country** and **Sub category** filters as needed.  
4. Toggle **Churn %** vs **Counts** for the heatmap table.

**Do not use** `live_seller_churn_dashboard_20260617.html` for current metrics — it uses outdated summary-card logic.

---

## 3. Repository files used by the dashboard

### 3.1 File map

| File | Role | Calculates churn? |
|------|------|-----------------|
| **`dashboard/live_seller_churn_dashboard_20260618.html`** | **Main dashboard** — UI, embedded data, all churn math | **Yes** |
| `data/raw/streams_first_stream_2026.csv` | Upstream stream extract (input) | No |
| `data/processed/canvas_data.json` | Seller/week JSON from build script | No |
| `scripts/build_canvas.py` | CSV → JSON ETL | No |
| `tools/check.js` | Copy of dashboard logic for headless tests | Same as HTML |
| `tools/harness.js` | Runs `compute()` smoke test | — |
| `scripts/build_html.py` | Legacy retention dashboard builder | Different definition |

### 3.2 Where churn is calculated (critical)

**All churn numbers in the current dashboard are computed in JavaScript inside one file:**

`dashboard/live_seller_churn_dashboard_20260618.html`

| JavaScript function | Responsibility |
|---------------------|----------------|
| **`compute()`** | Cohort assignment, gap churn array, new/growing/mature tenure churn counts |
| **`renderStats(res)`** | Top summary cards (weighted averages) |
| **`renderTable(res)`** | Cohort heatmap table |
| **`renderChart(res)`** | Cohort line chart (W4 / W10 / W16) |
| **`refresh()`** | Calls `compute()` then all render functions (on load and filter change) |

**No Python script calculates dashboard churn.** Python only prepares seller/week data from the CSV.

### 3.3 Data flow into the dashboard

```
data/raw/streams_first_stream_2026.csv
        ↓  scripts/build_canvas.py
data/processed/canvas_data.json
        ↓  embedded as const DATA = { ... } in HTML
dashboard/live_seller_churn_dashboard_20260618.html
        ↓  compute() in browser
Summary cards, heatmap, line chart
```

When you open the HTML file, seller stream weeks are already embedded. Filters and churn are recalculated instantly in the browser.

---

## 4. Dashboard page layout (section by section)

The page is organized top to bottom as follows.

### 4.1 Header banner

- eBay brand banner with title **“Live sellers churn analysis”**.
- Cosmetic only — no calculations.

### 4.2 Introduction text (below title)

Plain-language explanation of:

- What each **row** (cohort) represents  
- What **3-week churn** means in the table  
- Examples for W4, W5, W23  
- Definitions of **new / growing / mature seller churn** for summary cards  
- Note that cohorts 26RW21–26RW24 are hidden from the analysis  

This text mirrors the methodology documented in this guide.

### 4.3 Summary cards (top row — four boxes)

Rendered by **`renderStats()`**. Values come from **`compute()`** output.

#### Card 1: Total sellers

| Element | Description |
|---------|-------------|
| **Label** | Total sellers |
| **Value** | Sum of cohort sizes across all visible cohort rows |
| **Subtitle** | Country context (e.g. “all countries” or selected countries) |
| **Calculation** | `totals.onboard = sum(r.size)` for each cohort row after filters |
| **Does not** | Measure churn — count of sellers in analysis |

#### Card 2: New seller churn (at W4)

| Element | Description |
|---------|-------------|
| **Label** | New seller churn (at W4) |
| **Value** | Weighted average churn % |
| **Subtitle** | “Weighted avg · sellers with no stream in W1–W3 ÷ all starters · X / Y sellers” |
| **Tenure** | ~4 weeks (~1 month) since first stream week |
| **Churned if** | No stream in tenure weeks **W1, W2, or W3** |
| **Retained if** | At least one stream in any of W1, W2, W3 |

#### Card 3: Growing seller churn (at W10)

| Element | Description |
|---------|-------------|
| **Label** | Growing seller churn (at W10) |
| **Churned if** | No stream in tenure weeks **W7, W8, or W9** |
| **Tenure** | ~10 weeks (~2.5 months) |

#### Card 4: Mature seller churn (at W16)

| Element | Description |
|---------|-------------|
| **Label** | Mature seller churn (at W16) |
| **Churned if** | No stream in tenure weeks **W13, W14, or W15** |
| **Tenure** | ~16 weeks (~4 months) |

**Weighted average formula (all three churn cards):**

```
weighted_churn% = (sum of churned sellers across eligible cohorts)
                  ÷ (sum of starter counts across eligible cohorts) × 100
```

This is **not** a simple average of cohort percentages. Large cohorts weigh more.

**Eligibility** (cohort must have enough follow-up data):

| Card | Required follow-up |
|------|-------------------|
| New (W4) | `maxWeek − cohort ≥ 4` |
| Growing (W10) | `maxWeek − cohort ≥ 10` |
| Mature (W16) | `maxWeek − cohort ≥ 16` |

`maxWeek` is the latest retail week present in the filtered dataset (currently week 24).

### 4.4 Filter controls

Rendered dynamically by **`buildFilter()`**. Changing any filter calls **`refresh()`** → **`compute()`**.

#### Seller Country (multi-select)

- Source field: `SELLER_COUNTRY` from CSV → `DATA.countries[seller.c]`  
- Empty selection = **all countries**  
- **“Other Countries”** is excluded from dropdown options but included when no filter is applied  
- Effect: sellers not matching selected countries are **removed entirely**

#### Sub category (multi-select)

- Source field: `FCSD_VRTCL_SUP_GRP_revised`  
- Empty selection = all sub categories  
- Effect: only stream weeks in selected verticals count toward a seller’s week set  

**Important:** Sub category filter can change which retail weeks count and, in edge cases, which cohort week is assigned (see Section 8).

#### Cell values toggle

| Mode | Heatmap shows |
|------|----------------|
| **Churn %** (default) | `round(churned / cohort_size × 100)` |
| **Counts** | Raw number of churned sellers |

Only affects the **heatmap table**, not summary cards or line chart.

### 4.5 Cohort heatmap table

Rendered by **`renderTable()`** using `gapChurn[]` from **`compute()`**.

#### Columns

| Column | Meaning |
|--------|---------|
| **Cohort** | 26RWxx label + calendar date range (e.g. 1/4–1/10 '26) |
| **Sellers First Streamed on Live** | Cohort size (starters) |
| **W4, W5, W6, …** | 3-week gap churn at that tenure week |

Columns **W1–W3 are not shown** (insufficient history for 3-week look-back). Table starts at **W4**.

Empty cells: cohort has not yet reached that tenure week in the data.

#### 3-week gap churn (table definition)

For column **Wk** where **k ≥ 4**:

- Look-back tenure weeks: **W(k−3), W(k−2), W(k−1)**  
- Calendar retail weeks: **c+k−3, c+k−2, c+k−1** (where c = cohort week)  
- **Churned** if seller had **no stream** in any of those three weeks  
- **Retained** if seller streamed in **at least one** of those weeks  

| Table column | Look-back window (tenure) |
|--------------|---------------------------|
| W4 | W1, W2, W3 |
| W5 | W2, W3, W4 |
| W10 | W7, W8, W9 |
| W16 | W13, W14, W15 |
| W23 | W20, W21, W22 |

**Note:** Summary card “new seller churn” matches **W4 column** logic (W1–W3). Growing and mature cards use **fixed windows** (W7–W9 and W13–W15), which align with W10 and W16 column windows but are aggregated differently (weighted across cohorts).

#### Heatmap colors

Function: **`heatStyle(retention)`** where retention = `1 − churn_rate`.

- **Green** = low churn (high retention)  
- **Yellow / orange** = moderate churn  
- **Red** = high churn (≥ ~60% churn maps to full red)  

Color scale is compressed so typical churn (0–60%) uses the full spectrum.

### 4.6 Color legend (below table)

Gradient bar from **0% churn** (green) to **60%+ churn** (red). Explains heatmap cell shading only.

### 4.7 Cohort line chart

Rendered by **`renderChart()`**.

| Element | Description |
|---------|-------------|
| **Title** | Churn rate by cohort week |
| **Subtitle** | Per-cohort % at W4, W10, W16; mature line limited to cohorts with ≥16 weeks follow-up |
| **X-axis** | Cohort week (2026) — W01, W02, … |
| **Y-axis** | Churn rate (%) |
| **Blue line** | New seller churn % per cohort at W4 |
| **Yellow line** | Growing seller churn % per cohort at W10 |
| **Red line** | Mature seller churn % per cohort at W16 |

**Unlike summary cards**, each point is **unweighted per cohort:**

```
cohort_churn% = churned_count_for_that_milestone ÷ cohort_size × 100
```

Lines end where cohorts lack follow-up (mature line only spans earliest cohorts — typically through ~26RW08 with data through week 24).

No dots on lines — line-only chart for clarity.

---

## 5. Seller cohorts (2026)

### 5.1 Definition

A **cohort** is the **2026 retail week of a seller’s first Live stream**.

- Display label: **26RW01** through **26RW24**  
- **One seller belongs to exactly one cohort** — never double-counted across rows  
- Cohort assignment: **minimum `RETAIL_WEEK`** across all stream rows for that `SLR_ID`

### 5.2 How cohort is determined from source data

Each row in `data/raw/streams_first_stream_2026.csv` is **one stream event**:

| Column | Use |
|--------|-----|
| `SLR_ID` | Seller ID — group all rows per seller |
| `ID` | Stream/event ID (one stream per row) |
| `STRT_TM` | Stream start timestamp |
| `RETAIL_WEEK` | Retail week for this stream row |
| `first_stream_dt` | Seller’s first-ever Live date (same on all rows for seller) |

`scripts/build_canvas.py` collects all `(RETAIL_WEEK, vertical)` pairs per seller. The dashboard assigns cohort as **min(weeks)** — equivalent to the retail week of `first_stream_dt` / earliest `STRT_TM` in the current extract.

### 5.3 Excluded cohorts

Cohorts **21, 22, 23, 24** (26RW21–26RW24) are **hidden** in the dashboard:

```javascript
const EXCLUDED_COHORTS = new Set([21, 22, 23, 24]);
```

Reason: those sellers have not been on Live long enough for fair comparison at later tenure milestones.

### 5.4 Current population (typical extract)

- ~**2,570** sellers  
- Retail weeks **1–24** in data  
- Countries: UK, IT, US, DE, FR, AU, CA, Other Countries  

---

## 6. Retail weeks and tenure

### 6.1 Retail week calendar (2026)

Retail weeks run **Sunday through Saturday**. Week 1 begins **January 4, 2026**.

| Label | Dates (2026) |
|-------|----------------|
| 26RW01 | Jan 4 – Jan 10 |
| 26RW02 | Jan 11 – Jan 17 |
| 26RW03 | Jan 18 – Jan 24 |
| 26RW04 | Jan 25 – Jan 31 |
| 26RW05 | Feb 1 – Feb 7 |
| 26RW06 | Feb 8 – Feb 14 |
| 26RW07 | Feb 15 – Feb 21 |
| 26RW08 | Feb 22 – Feb 28 |
| 26RW09 | Mar 1 – Mar 7 |
| 26RW10 | Mar 8 – Mar 14 |
| 26RW11 | Mar 15 – Mar 21 |
| 26RW12 | Mar 22 – Mar 28 |
| 26RW13 | Mar 29 – Apr 4 |
| 26RW14 | Apr 5 – Apr 11 |
| 26RW15 | Apr 12 – Apr 18 |
| 26RW16 | Apr 19 – Apr 25 |
| 26RW17 | Apr 26 – May 2 |
| 26RW18 | May 3 – May 9 |
| 26RW19 | May 10 – May 16 |
| 26RW20 | May 17 – May 23 |
| 26RW21 | May 24 – May 30 |
| 26RW22 | May 31 – Jun 6 |
| 26RW23 | Jun 7 – Jun 13 |
| 26RW24 | Jun 14 – Jun 20 |

### 6.2 Tenure week notation

If a seller’s cohort retail week is **c**:

| Tenure label | Calendar retail week |
|--------------|----------------------|
| W1 | c + 1 |
| W2 | c + 2 |
| Wk | c + k |

**W4** ≈ 1 month after first stream week  
**W10** ≈ 2.5 months  
**W16** ≈ 4 months  

Tenure weeks are **not** “weeks since first stream event within the same calendar week” — they follow the **retail week calendar**.

---

## 7. Churn calculations in detail (`compute()`)

Location in HTML: function **`compute()`** (~line 333).

### 7.1 Constants

```javascript
const EARLY_AT = 4, MID_AT = 10, MATURE_AT = 16;
const EXCLUDED_COHORTS = new Set([21, 22, 23, 24]);
```

### 7.2 Step 1 — Filter sellers and build cohort buckets

For each seller in embedded `DATA.sellers`:

1. If country filter active → skip if `DATA.countries[s.c]` not selected.  
2. Build `weeks` = set of retail weeks from `s.wv` pairs, optionally filtered by sub category.  
3. Skip seller if `weeks` is empty after vertical filter.  
4. `cohort = min(weeks)`.  
5. Skip if `cohort ∈ EXCLUDED_COHORTS`.  
6. Append `weeks` set to `cohortMembers[cohort]`.  
7. Track `maxWeek` = latest retail week seen; `minWeek` = earliest cohort shown.

### 7.3 Step 2 — Per-cohort metrics

For each cohort `c` with member list `mem` (each member is a set of retail weeks):

**Cohort size:** `size = mem.length`

**Gap churn array (`gapChurn[k]`)** for k = 0 … maxWeek − c:

- If k < 4: `null` (no table column)  
- Else: count sellers with **no** stream in weeks `c+k−3`, `c+k−2`, `c+k−1`  
- `gapChurn[k] = size − retained_count`

**New seller churn (`earlyTenureChurn`)** — if `maxWeek − c ≥ 4`:

- Retained if any stream in weeks `c+1`, `c+2`, `c+3`  
- `earlyTenureChurn = size − retained`

**Growing seller churn (`midTenureChurn`)** — if `maxWeek − c ≥ 10`:

- Retained if any stream in weeks `c+7`, `c+8`, `c+9`  
- `midTenureChurn = size − retained`

**Mature seller churn (`matureTenureChurn`)** — if `maxWeek − c ≥ 16`:

- Retained if any stream in weeks `c+13`, `c+14`, `c+15`  
- `matureTenureChurn = size − retained`

### 7.4 Retention rule (all metrics)

- **One stream** anywhere in the look-back window → **retained** (not churned)  
- **Zero streams** in the entire window → **churned**  
- Comebacks: if a seller streams again within the window, they count as retained for that measurement point  

### 7.5 `compute()` return object

```javascript
{
  rows: [ { c, size, gapChurn[], earlyTenureChurn, midTenureChurn, matureTenureChurn }, ... ],
  maxWeek, minWeek,
  totals: { onboard: total_seller_count }
}
```

---

## 8. Embedded data structure (`const DATA`)

The HTML embeds JSON equivalent to `data/processed/canvas_data.json`:

```json
{
  "countries": ["UK", "IT", "US", ...],
  "tiers": [...],
  "orgs": [...],
  "verticals": ["Trading Cards CCG", ...],
  "sellers": [
    {
      "c": 0,
      "t": 2,
      "o": 1,
      "wv": [[5, 3], [6, 3], [10, 12]]
    }
  ]
}
```

| Field | Meaning |
|-------|---------|
| `c`, `t`, `o` | Indices into `countries`, `tiers`, `orgs` arrays |
| `wv` | List of `[retail_week, vertical_index]` for each week the seller streamed |

**No churn fields are pre-computed** in JSON — all churn is derived at runtime.

---

## 9. Filters and edge cases

### 9.1 Country filter

Excludes non-matching sellers completely. Does not affect cohort assignment for included sellers.

### 9.2 Sub category filter

Only stream weeks in selected verticals are kept. Effects:

- Retention/churn based on streaming **in that category**  
- If first stream was outside selected verticals, cohort week may become the earliest week **in the filtered vertical**, not true first-stream cohort  

### 9.3 Mature churn sample size

With data through retail week 24, only cohorts **1–8** typically have ≥16 weeks follow-up. Mature seller metrics use a **smaller denominator** than new seller metrics.

### 9.4 Line chart vs summary cards

| View | Aggregation |
|------|-------------|
| Summary cards | **Weighted** across cohorts |
| Line chart | **Per-cohort** % (unweighted) |
| Heatmap | **Per-cohort** % or count per cell |

---

## 10. Building and refreshing data

### 10.1 Regenerate JSON from CSV

```bash
python scripts/build_canvas.py
```

Reads: `data/raw/streams_first_stream_2026.csv`  
Writes: `data/processed/canvas_data.json`

### 10.2 Update dashboard data

Replace the `const DATA = …` block in `dashboard/live_seller_churn_dashboard_20260618.html` with contents of `canvas_data.json`.

### 10.3 Validate logic (optional)

```bash
cd tools && node harness.js
```

### 10.4 Maintenance checklist

1. Replace `data/raw/streams_first_stream_2026.csv`  
2. Run `python scripts/build_canvas.py`  
3. Re-embed JSON into dashboard HTML  
4. Open dashboard — verify total sellers and card denominators  
5. If churn **definitions** change → edit **`compute()`** in HTML (sync `tools/check.js` if used)  
6. Regenerate Word docs: `python scripts/build_documentation_docx.py`  

---

## 11. Formula quick reference

```
c = cohort retail week (seller's first stream week)

NEW SELLER (W4):     churned ⟺ no stream in weeks c+1, c+2, c+3
GROWING (W10):       churned ⟺ no stream in weeks c+7, c+8, c+9
MATURE (W16):        churned ⟺ no stream in weeks c+13, c+14, c+15

HEATMAP at Wk (k≥4): churned ⟺ no stream in weeks c+k-3, c+k-2, c+k-1

SUMMARY CARD %:      Σ(churned) / Σ(starters) × 100  (weighted)
LINE CHART %:        churned / cohort_size × 100     (per cohort)
HEATMAP CELL %:      gapChurn[k] / cohort_size × 100
HEATMAP CELL COUNT:  gapChurn[k]
```

---

## 12. Glossary

| Term | Definition |
|------|------------|
| **Cohort** | Sellers who first streamed Live in the same 2026 retail week |
| **Tenure week Wk** | Retail week `c + k` relative to cohort week `c` |
| **Churned** | No stream in the defined look-back window |
| **Retained** | At least one stream in the look-back window |
| **Gap churn** | Table metric: 3-week look-back from each column Wk |
| **Weighted average** | Sum of churned ÷ sum of starters across cohorts |
| **maxWeek** | Latest retail week in filtered data |
| **Starter** | Seller in cohort row at initial cohort size |

---

## 13. Which file to edit for common tasks

| Task | File / function |
|------|-----------------|
| Change churn definitions | `dashboard/...20260618.html` → `compute()` |
| Change summary card labels or weighting | `renderStats()` |
| Change heatmap | `renderTable()`, `heatStyle()` |
| Change line chart | `renderChart()` |
| Add source data | `data/raw/streams_first_stream_2026.csv` |
| Rebuild seller JSON | `scripts/build_canvas.py` |
| Test without browser | `tools/harness.js` |

---

*End of Live Seller Churn Dashboard Guide*
