# Live Seller Churn Analysis — Documentation

**Dashboard:** `dashboard/live_seller_churn_dashboard_20260618.html`  
**Repository:** https://github.com/devkashikar/live-seller-churn-analysis

---

## How churn is calculated (most important)

All churn metrics are computed in the browser by **`compute()`** in `dashboard/live_seller_churn_dashboard_20260618.html`. No Python file calculates dashboard churn.

### Core rule

A seller is **churned** for a given check if they had **no live stream** in the defined **week window**.  
A seller is **retained** if they streamed in **at least one** week in that window.

Churn is a **point-in-time snapshot** per column or card. If a seller streams again within the window, they count as retained for that measurement.

### Tenure weeks

Sellers are grouped into **cohorts** by the **2026 retail week of their first Live stream** (cohort week `c`).

| Tenure label | Calendar retail week |
|--------------|----------------------|
| W1 | c + 1 |
| Wk | c + k |

Example: cohort 26RW05 (`c = 5`) → W7 is retail week 12.

### Three summary-card churn metrics (weighted averages)

Cards show **weighted** churn: `sum(churned sellers) ÷ sum(starters) × 100` across eligible cohorts (not a simple average of cohort %).

| Card | Measured at | Churned = no stream in | ~Tenure | Eligible when |
|------|-------------|------------------------|---------|---------------|
| **New seller churn** | W4 | **W1, W2, W3** | ~1 month | `maxWeek − cohort ≥ 4` |
| **Growing seller churn** | W10 | **W7, W8, W9** | ~2.5 months | `maxWeek − cohort ≥ 10` |
| **Mature seller churn** | W16 | **W13, W14, W15** | ~4 months | `maxWeek − cohort ≥ 16` |

**Calendar weeks checked (for cohort `c`):**

| Card | Retail weeks checked |
|------|---------------------|
| New (W4) | c+1, c+2, c+3 |
| Growing (W10) | c+7, c+8, c+9 |
| Mature (W16) | c+13, c+14, c+15 |

### Heatmap table — 3-week gap churn (from W4)

Each column **Wk** (`k ≥ 4`) uses a **rolling 3-week look-back**:

- **Churned** if no stream in tenure weeks **W(k−3), W(k−2), W(k−1)**
- Calendar weeks: **c+k−3, c+k−2, c+k−1**

| Column | Window (tenure weeks) |
|--------|----------------------|
| W4 | W1, W2, W3 |
| W5 | W2, W3, W4 |
| W10 | W7, W8, W9 |
| W16 | W13, W14, W15 |

Cell value = **Churn %** (`churned ÷ cohort size`) or **Counts** (raw churned count). Columns W1–W3 are blank.

**Note:** New seller card (W4) uses the same window as the **W4 column**. Growing and mature cards use fixed windows (W7–W9, W13–W15), not necessarily the same as a single heatmap column label.

### Line chart

Per-cohort **unweighted** churn % at W4, W10, and W16 (same windows as summary cards). Mature line only includes cohorts with ≥16 weeks of data.

### Formula reference

```
c = cohort retail week (seller's first stream week in 2026)

NEW (W4):      churned ⟺ no stream in weeks c+1, c+2, c+3
GROWING (W10): churned ⟺ no stream in weeks c+7, c+8, c+9
MATURE (W16):  churned ⟺ no stream in weeks c+13, c+14, c+15

HEATMAP Wk:    churned ⟺ no stream in weeks c+k-3, c+k-2, c+k-1  (k ≥ 4)

SUMMARY CARD:  Σ(churned) / Σ(starters) × 100
HEATMAP CELL:  gapChurn[k] / cohort_size × 100
```

### Where in code

| Function | Role |
|----------|------|
| **`compute()`** | Assigns cohorts; calculates `gapChurn`, `earlyTenureChurn`, `midTenureChurn`, `matureTenureChurn` |
| **`renderStats()`** | Summary cards (weighted averages) |
| **`renderTable()`** | Heatmap from `gapChurn[]` |
| **`renderChart()`** | Per-cohort lines at W4 / W10 / W16 |

Constants in `compute()`:

```javascript
const EARLY_AT = 4, MID_AT = 10, MATURE_AT = 16;
const EXCLUDED_COHORTS = new Set([21, 22, 23, 24]);
```

---

## Seller cohorts

- **Cohort** = retail week of seller’s **first Live stream** in 2026 (`26RW01` … `26RW24`).
- **One seller → one cohort** (`cohort = min(RETAIL_WEEK)` per `SLR_ID`).
- **Excluded from dashboard:** cohorts 21–24 (insufficient follow-up).
- **~2,570 sellers** in current extract; data through retail week 24.

**Source data:** each CSV row is one stream (`ID` = stream id, `SLR_ID` = seller). Cohort uses minimum `RETAIL_WEEK` across all rows for that seller (matches `first_stream_dt` / earliest `STRT_TM`).

---

## Dashboard sections

| Section | What it shows | Calculation source |
|---------|---------------|-------------------|
| **Total sellers** | Count across cohort rows | `sum(cohort sizes)` — not churn |
| **Summary cards (4)** | Total + 3 weighted churn % | `renderStats()` ← `compute()` |
| **Country / Sub category filters** | Subset of sellers/streams | Re-runs `compute()` |
| **Churn % / Counts toggle** | Heatmap display mode | `renderTable()` only |
| **Heatmap table** | Cohort rows × W4+ columns | `gapChurn[]` from `compute()` |
| **Color legend** | Green (low churn) → red (high) | `heatStyle()` |
| **Line chart** | Cohort week vs churn % | Per-cohort % from `compute()` |

Retail weeks are **Sunday–Saturday**; 26RW01 = Jan 4–10, 2026. Full calendar is in dashboard HTML (`RW_DATES`).

---

## Project files

```
data/raw/streams_first_stream_2026.csv     ← INPUT (stream extract)
data/processed/canvas_data.json            ← built by scripts/build_canvas.py
dashboard/live_seller_churn_dashboard_20260618.html  ← DASHBOARD + churn math
scripts/build_canvas.py                    ← CSV → JSON (no churn)
tools/check.js, tools/harness.js           ← optional validation
```

| File | Calculates churn? |
|------|-------------------|
| `dashboard/live_seller_churn_dashboard_20260618.html` | **Yes — all metrics** |
| `scripts/build_canvas.py` | No — ETL only |
| `data/raw/*.csv`, `data/processed/*.json` | No — raw / structured data |

**Data flow:** CSV → `build_canvas.py` → JSON → embedded as `const DATA` in HTML → `compute()` in browser.

---

## Filters and edge cases

- **Country:** removes sellers not matching selection. "Other Countries" hidden from dropdown but included when filter is empty (All).
- **Sub category:** only streams in selected verticals count toward week sets; can affect cohort in edge cases.
- **Mature churn** has a smaller denominator (only early cohorts reach W16 with data through week 24).
- **Comebacks:** streaming within the look-back window = retained for that measurement.

---

## Quick start

```bash
# Open dashboard
open dashboard/live_seller_churn_dashboard_20260618.html

# Refresh JSON from CSV
python scripts/build_canvas.py
# Then re-embed data/processed/canvas_data.json into the HTML const DATA block

# Regenerate this Word document
python scripts/build_documentation_docx.py
```

---

## Maintenance

1. Update `data/raw/streams_first_stream_2026.csv`
2. Run `python scripts/build_canvas.py`
3. Re-embed JSON into dashboard HTML
4. To **change churn definitions**, edit **`compute()`** in the dashboard HTML
5. Run `python scripts/build_documentation_docx.py` to refresh this document

---

## Glossary

| Term | Meaning |
|------|---------|
| Cohort | Sellers whose first Live stream was in the same 2026 retail week |
| Tenure week Wk | Retail week `c + k` relative to cohort week `c` |
| Churned | No stream in the defined week window |
| Retained | At least one stream in the window |
| Weighted average | Sum of churned ÷ sum of starters across cohorts |
| maxWeek | Latest retail week in the filtered dataset |
