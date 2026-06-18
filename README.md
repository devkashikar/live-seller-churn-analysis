# Live Seller Churn Analysis

Interactive dashboard for **eBay Live seller churn** in 2026 — cohort retention, tenure milestones, and rolling 3-week churn.

**Dashboard:** [`dashboard/live_seller_churn_dashboard_20260618.html`](dashboard/live_seller_churn_dashboard_20260618.html)  
**Word documentation:** [`documentation/Live_Seller_Churn_Analysis_Documentation.docx`](documentation/Live_Seller_Churn_Analysis_Documentation.docx)  
**Repository:** [github.com/devkashikar/live-seller-churn-analysis](https://github.com/devkashikar/live-seller-churn-analysis)

## Churn (summary)

All churn is calculated in **`compute()`** inside the dashboard HTML (not Python).

| Metric | At | Churned = no stream in |
|--------|-----|------------------------|
| New seller | W4 | W1, W2, W3 |
| Growing seller | W10 | W7, W8, W9 |
| Mature seller | W16 | W13, W14, W15 |

**Heatmap (W4+):** 3-week look-back — at Wk, churned if no stream in W(k−3), W(k−2), W(k−1).

Summary cards use **weighted** averages: `Σ churned ÷ Σ starters`. Full definitions, formulas, file map, and dashboard sections are in the Word doc and `documentation/documentation_source.md`.

## Project layout

```
data/raw/streams_first_stream_2026.csv       # Input CSV
data/processed/canvas_data.json              # Built JSON
dashboard/live_seller_churn_dashboard_20260618.html  # Main dashboard
documentation/Live_Seller_Churn_Analysis_Documentation.docx
scripts/build_canvas.py                      # CSV → JSON
scripts/build_documentation_docx.py          # Markdown → Word doc
tools/check.js, tools/harness.js             # Validation helpers
```

## Quick start

```bash
open dashboard/live_seller_churn_dashboard_20260618.html
python scripts/build_canvas.py              # refresh JSON from CSV
python scripts/build_documentation_docx.py  # refresh Word doc
```
