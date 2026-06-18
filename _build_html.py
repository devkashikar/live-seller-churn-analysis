import json

with open("_canvas_data.json", "r", encoding="utf-8") as f:
    data_js = f.read()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cohort Retention — eBay Live (RWB 2026)</title>
<style>
  :root {
    --bg: #f4f5f7;
    --panel: #ffffff;
    --ink: #1b2733;
    --muted: #6b7785;
    --line: #e1e5ea;
    --accent: #2f6fed;
    --accent-soft: #eaf1fe;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 1500px; margin: 0 auto; padding: 24px 28px 56px; }
  h1 { font-size: 22px; font-weight: 650; margin: 0 0 4px; letter-spacing: -0.2px; }
  .sub { color: var(--muted); font-size: 12.5px; margin: 0 0 20px; max-width: 980px; line-height: 1.5; }

  /* summary cards */
  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 22px; }
  .stat {
    background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
    padding: 14px 16px;
  }
  .stat .label { color: var(--muted); font-size: 11.5px; text-transform: uppercase; letter-spacing: .04em; }
  .stat .value { font-size: 28px; font-weight: 680; margin-top: 4px; letter-spacing: -0.5px; }
  .stat.onboard .value { color: var(--ink); }
  .stat.active .value { color: #1a9f57; }
  .stat.churn .value { color: #d23f3f; }
  .stat.ret .value { color: var(--accent); }

  /* controls */
  .controls {
    display: flex; flex-wrap: wrap; align-items: flex-end; gap: 14px;
    background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
    padding: 14px 16px; margin-bottom: 18px;
  }
  .filter { position: relative; min-width: 210px; }
  .filter > .flabel { display: block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 5px; }
  .ms-btn {
    width: 100%; text-align: left; background: #fff; border: 1px solid var(--line);
    border-radius: 7px; padding: 7px 10px; font-size: 13px; cursor: pointer;
    display: flex; justify-content: space-between; align-items: center; gap: 8px; color: var(--ink);
  }
  .ms-btn:hover { border-color: #c5ccd4; }
  .ms-btn .caret { color: var(--muted); font-size: 10px; }
  .ms-panel {
    position: absolute; z-index: 30; top: calc(100% + 4px); left: 0; min-width: 100%;
    max-width: 340px; background: #fff; border: 1px solid var(--line); border-radius: 8px;
    box-shadow: 0 6px 22px rgba(20,30,45,.12); padding: 8px; display: none; max-height: 320px; overflow: auto;
  }
  .ms-panel.open { display: block; }
  .ms-actions { display: flex; gap: 8px; margin-bottom: 6px; padding: 2px 2px 6px; border-bottom: 1px solid var(--line); }
  .ms-actions button {
    flex: 1; font-size: 11.5px; padding: 4px 6px; border: 1px solid var(--line);
    background: #fff; border-radius: 6px; cursor: pointer; color: var(--accent);
  }
  .ms-actions button:hover { background: var(--accent-soft); }
  .ms-opt { display: flex; align-items: center; gap: 8px; padding: 5px 6px; border-radius: 6px; cursor: pointer; font-size: 12.5px; }
  .ms-opt:hover { background: #f4f6f9; }
  .ms-opt input { accent-color: var(--accent); width: 14px; height: 14px; }
  .ms-opt span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  .mode { margin-left: auto; display: flex; align-items: flex-end; gap: 10px; }
  .seg { display: inline-flex; border: 1px solid var(--line); border-radius: 7px; overflow: hidden; }
  .seg button { border: none; background: #fff; padding: 7px 14px; font-size: 12.5px; cursor: pointer; color: var(--muted); }
  .seg button.active { background: var(--accent); color: #fff; }

  /* table */
  .tablewrap { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; overflow: auto; max-height: 72vh; }
  table { border-collapse: separate; border-spacing: 0; font-size: 12px; width: max-content; min-width: 100%; }
  th, td { padding: 0; text-align: center; white-space: nowrap; }
  thead th {
    position: sticky; top: 0; z-index: 5; background: #f0f2f5; color: var(--muted);
    font-weight: 600; font-size: 11px; border-bottom: 1px solid var(--line); padding: 8px 8px;
  }
  tbody td { border-bottom: 1px solid #eef1f4; height: 26px; padding: 0 6px; }
  /* sticky meta columns */
  .col-cohort { position: sticky; left: 0; z-index: 4; background: #fff; text-align: left; font-weight: 600;
    min-width: 76px; padding-left: 14px !important; border-right: 1px solid var(--line); }
  thead .col-cohort { z-index: 7; background: #f0f2f5; }
  .col-meta { background: #fff; color: var(--ink); min-width: 58px; font-variant-numeric: tabular-nums; }
  thead .col-meta { background: #f0f2f5; }
  .heat { color: #fff; font-variant-numeric: tabular-nums; font-weight: 600; min-width: 40px; }
  tbody tr:hover .col-cohort, tbody tr:hover .col-meta { background: #f7f9fc; }
  .total td { font-weight: 700; background: #eef1f5; border-top: 2px solid var(--line); }
  .total .col-cohort { background: #eef1f5; }
  .legend { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 11.5px; margin-top: 12px; }
  .legend .bar { height: 10px; width: 160px; border-radius: 5px;
    background: linear-gradient(to right, hsl(0,65%,46%), hsl(60,65%,46%), hsl(120,65%,42%)); }
  .foot { color: var(--muted); font-size: 11px; margin-top: 16px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>Cohort Retention — eBay Live</h1>
  <p class="sub">
    Each row is a cohort of sellers grouped by the <b>first 2026 retail week they streamed</b> (after applying the filters below).
    Reading across a row, <b>W0</b> is the cohort's starting size and each later <b>W<i>k</i></b> column counts how many of those same sellers
    streamed again <i>k</i> weeks later. Use the toggle to switch cells between seller counts and retention %.
    Cells are shaded by retention rate (red = low, green = high). Source: eBay Live streams, RWB 2026, retail weeks 1–24.
  </p>

  <div class="stats" id="stats"></div>

  <div class="controls" id="controls">
    <div class="filter" data-key="country"><label class="flabel">Seller Country</label></div>
    <div class="filter" data-key="tier"><label class="flabel">Seller Tier Tranche</label></div>
    <div class="filter" data-key="org"><label class="flabel">Org</label></div>
    <div class="filter" data-key="vert"><label class="flabel">FCSD Vertical (Sup Grp, revised)</label></div>
    <div class="mode">
      <div>
        <label class="flabel" style="display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.04em;margin-bottom:5px;">Cell values</label>
        <div class="seg" id="modeSeg">
          <button data-mode="count" class="active">Counts</button>
          <button data-mode="pct">Retention %</button>
        </div>
      </div>
    </div>
  </div>

  <div class="tablewrap"><table id="grid"></table></div>

  <div class="legend"><span>0%</span><span class="bar"></span><span>100% retained</span></div>
  <p class="foot" id="foot"></p>
</div>

<script>
const DATA = /*__DATA__*/;

const state = { country: [], tier: [], org: [], vert: [], mode: "count" };

const FILTERS = [
  { key: "country", source: "countries" },
  { key: "tier",    source: "tiers" },
  { key: "org",     source: "orgs" },
  { key: "vert",    source: "verticals" },
];

function optionsFor(source) {
  // unique, sorted; empty-string label shown as "(blank)"
  const arr = DATA[source].slice().sort((a, b) => String(a).localeCompare(String(b)));
  return arr;
}

function pad2(n) { return n < 10 ? "0" + n : "" + n; }
function cohortLabel(w) { return "26RW" + pad2(w); }

function heatStyle(p) {
  // p in [0,1] -> red(0) to green(120)
  const hue = Math.max(0, Math.min(1, p)) * 120;
  return "background:hsl(" + hue.toFixed(0) + ",65%," + (p >= 0.5 ? 42 : 46) + "%);";
}

function compute() {
  const sets = {
    country: new Set(state.country), tier: new Set(state.tier),
    org: new Set(state.org), vert: new Set(state.vert),
  };
  const use = {
    country: state.country.length > 0, tier: state.tier.length > 0,
    org: state.org.length > 0, vert: state.vert.length > 0,
  };
  const cohortMembers = {};
  let maxWeek = 0, minWeek = Infinity;

  for (const s of DATA.sellers) {
    if (use.country && !sets.country.has(DATA.countries[s.c])) continue;
    if (use.tier && !sets.tier.has(DATA.tiers[s.t])) continue;
    if (use.org && !sets.org.has(DATA.orgs[s.o])) continue;
    const weeks = new Set();
    for (const pair of s.wv) {
      if (use.vert && !sets.vert.has(DATA.verticals[pair[1]])) continue;
      weeks.add(pair[0]);
    }
    if (weeks.size === 0) continue;
    let cohort = Infinity;
    weeks.forEach(w => { if (w < cohort) cohort = w; if (w > maxWeek) maxWeek = w; });
    if (cohort < minWeek) minWeek = cohort;
    (cohortMembers[cohort] = cohortMembers[cohort] || []).push(weeks);
  }

  if (minWeek === Infinity) {
    return { rows: [], maxWeek: 0, minWeek: 0, totals: { onboard: 0, active: 0, churned: 0 } };
  }

  const cohortWeeks = Object.keys(cohortMembers).map(Number).sort((a, b) => a - b);
  const rows = [];
  let tOn = 0, tAct = 0;
  for (const c of cohortWeeks) {
    const mem = cohortMembers[c];
    const size = mem.length;
    let active = 0;
    for (const m of mem) if (m.has(maxWeek)) active++;
    tOn += size; tAct += active;
    const cells = [];
    for (let k = 0; k <= maxWeek - c; k++) {
      let cnt = 0;
      for (const m of mem) if (m.has(c + k)) cnt++;
      cells.push(cnt);
    }
    rows.push({ c: c, size: size, active: active, churned: size - active, cells: cells });
  }
  return { rows: rows, maxWeek: maxWeek, minWeek: minWeek, totals: { onboard: tOn, active: tAct, churned: tOn - tAct } };
}

function renderStats(res) {
  const ret = res.totals.onboard ? (100 * res.totals.active / res.totals.onboard) : 0;
  const wk = res.maxWeek || 0;
  const cards = [
    { cls: "onboard", label: "Total Onboarded", value: res.totals.onboard.toLocaleString() },
    { cls: "active",  label: "Active in latest week (RW" + wk + ")", value: res.totals.active.toLocaleString() },
    { cls: "churn",   label: "Churned", value: res.totals.churned.toLocaleString() },
    { cls: "ret",     label: "Retention Rate", value: ret.toFixed(1) + "%" },
  ];
  document.getElementById("stats").innerHTML = cards.map(c =>
    '<div class="stat ' + c.cls + '"><div class="label">' + c.label + '</div><div class="value">' + c.value + '</div></div>'
  ).join("");
}

function renderTable(res) {
  const grid = document.getElementById("grid");
  if (!res.rows.length) {
    grid.innerHTML = '<thead><tr><th class="col-cohort">No data</th></tr></thead>';
    return;
  }
  const nCols = res.maxWeek - res.minWeek + 1; // W0 .. W(max-min)
  const wkLabel = res.maxWeek;

  let head = '<thead><tr>';
  head += '<th class="col-cohort">Cohort</th>';
  head += '<th class="col-meta">Sellers<br>Onboarded</th>';
  head += '<th class="col-meta">Active<br>(RW' + wkLabel + ')</th>';
  head += '<th class="col-meta">Churned</th>';
  for (let k = 0; k < nCols; k++) head += '<th>W' + k + '</th>';
  head += '</tr></thead>';

  let body = '<tbody>';
  for (const r of res.rows) {
    body += '<tr>';
    body += '<td class="col-cohort">' + cohortLabel(r.c) + '</td>';
    body += '<td class="col-meta">' + r.size + '</td>';
    body += '<td class="col-meta">' + r.active + '</td>';
    body += '<td class="col-meta">' + r.churned + '</td>';
    for (let k = 0; k < nCols; k++) {
      if (k < r.cells.length) {
        const cnt = r.cells[k];
        const p = r.size ? cnt / r.size : 0;
        const txt = state.mode === "pct" ? Math.round(p * 100) + "%" : cnt;
        body += '<td class="heat" style="' + heatStyle(p) + '">' + txt + '</td>';
      } else {
        body += '<td></td>';
      }
    }
    body += '</tr>';
  }
  // total row
  body += '<tr class="total">';
  body += '<td class="col-cohort">TOTAL</td>';
  body += '<td class="col-meta">' + res.totals.onboard + '</td>';
  body += '<td class="col-meta">' + res.totals.active + '</td>';
  body += '<td class="col-meta">' + res.totals.churned + '</td>';
  for (let k = 0; k < nCols; k++) body += '<td></td>';
  body += '</tr></tbody>';

  grid.innerHTML = head + body;
}

function refresh() {
  const res = compute();
  renderStats(res);
  renderTable(res);
  document.getElementById("foot").textContent =
    "Showing " + res.rows.length + " weekly cohorts · weeks " +
    (res.minWeek || "-") + "–" + (res.maxWeek || "-") +
    " · cohort = first 2026 retail week a seller streamed under current filters.";
}

/* ---------- multi-select dropdowns ---------- */
function summaryText(key) {
  const sel = state[key];
  if (!sel.length) return "All";
  if (sel.length === 1) return sel[0] === "" ? "(blank)" : sel[0];
  return sel.length + " selected";
}

function buildFilter(filterEl, key, source) {
  const opts = optionsFor(source);

  const btn = document.createElement("button");
  btn.className = "ms-btn";
  btn.type = "button";
  btn.innerHTML = '<span class="ms-summary"></span><span class="caret">&#9662;</span>';

  const panel = document.createElement("div");
  panel.className = "ms-panel";

  const actions = document.createElement("div");
  actions.className = "ms-actions";
  const allBtn = document.createElement("button"); allBtn.type = "button"; allBtn.textContent = "Select all";
  const clrBtn = document.createElement("button"); clrBtn.type = "button"; clrBtn.textContent = "Clear (All)";
  actions.appendChild(allBtn); actions.appendChild(clrBtn);
  panel.appendChild(actions);

  const optEls = [];
  for (const o of opts) {
    const row = document.createElement("label");
    row.className = "ms-opt";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.value = o;
    const span = document.createElement("span");
    span.textContent = o === "" ? "(blank)" : o;
    span.title = span.textContent;
    row.appendChild(cb); row.appendChild(span);
    panel.appendChild(row);
    optEls.push(cb);
    cb.addEventListener("change", () => {
      state[key] = optEls.filter(c => c.checked).map(c => c.value);
      updateSummary();
      refresh();
    });
  }

  function updateSummary() { btn.querySelector(".ms-summary").textContent = summaryText(key); }
  function syncChecks() { const set = new Set(state[key]); optEls.forEach(c => c.checked = set.has(c.value)); }

  allBtn.addEventListener("click", () => { state[key] = opts.slice(); syncChecks(); updateSummary(); refresh(); });
  clrBtn.addEventListener("click", () => { state[key] = []; syncChecks(); updateSummary(); refresh(); });

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = panel.classList.contains("open");
    document.querySelectorAll(".ms-panel.open").forEach(p => p.classList.remove("open"));
    if (!open) panel.classList.add("open");
  });
  panel.addEventListener("click", (e) => e.stopPropagation());

  filterEl.appendChild(btn);
  filterEl.appendChild(panel);
  updateSummary();
}

document.addEventListener("click", () => {
  document.querySelectorAll(".ms-panel.open").forEach(p => p.classList.remove("open"));
});

FILTERS.forEach(f => {
  const el = document.querySelector('.filter[data-key="' + f.key + '"]');
  buildFilter(el, f.key, f.source);
});

document.querySelectorAll("#modeSeg button").forEach(b => {
  b.addEventListener("click", () => {
    state.mode = b.getAttribute("data-mode");
    document.querySelectorAll("#modeSeg button").forEach(x => x.classList.remove("active"));
    b.classList.add("active");
    refresh();
  });
});

refresh();
</script>
</body>
</html>
"""

out = HTML.replace("/*__DATA__*/", data_js)
with open("cohort_retention_dashboard.html", "w", encoding="utf-8") as f:
    f.write(out)
print("wrote cohort_retention_dashboard.html", len(out), "bytes")
