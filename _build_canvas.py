import csv, json, collections, os

CSV = "streams_first_stream_2026.csv"

countries, tiers, orgs, verticals = [], [], [], []
ci, ti, oi, vi = {}, {}, {}, {}

def idx(val, arr, m):
    if val not in m:
        m[val] = len(arr)
        arr.append(val)
    return m[val]

# seller -> attrs + set of (week, vert)
sellers = {}  # slr_id -> {"c":..,"t":..,"o":..,"wv":set()}

with open(CSV, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        if row["RETAIL_WEEK"] == "53":
            continue
        s = row["SLR_ID"]
        c = idx(row["SELLER_COUNTRY"], countries, ci)
        t = idx(row["Seller_Tier_Tranche"], tiers, ti)
        o = idx(row["Org"], orgs, oi)
        v = idx(row["FCSD_VRTCL_SUP_GRP_revised"], verticals, vi)
        w = int(row["RETAIL_WEEK"])
        rec = sellers.get(s)
        if rec is None:
            rec = {"c": c, "t": t, "o": o, "wv": set()}
            sellers[s] = rec
        rec["wv"].add((w, v))

seller_list = []
for s, rec in sellers.items():
    wv = sorted(rec["wv"])
    seller_list.append({"c": rec["c"], "t": rec["t"], "o": rec["o"], "wv": [[w, v] for (w, v) in wv]})

data = {
    "countries": countries,
    "tiers": tiers,
    "orgs": orgs,
    "verticals": verticals,
    "sellers": seller_list,
}

js = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
print("sellers:", len(seller_list), "| json bytes:", len(js.encode("utf-8")))

# ---- sanity check: no-filter cohort matrix ----
cohort_members = collections.defaultdict(list)
maxw = 0
for sd in seller_list:
    weeks = set(w for (w, v) in sd["wv"])
    cohort = min(weeks)
    maxw = max(maxw, max(weeks))
    cohort_members[cohort].append(weeks)

onboard = active = 0
print("maxweek:", maxw)
print("cohort | size | activeLast | W0 W1 W2 W3 W4")
for c in sorted(cohort_members):
    mem = cohort_members[c]
    size = len(mem)
    al = sum(1 for m in mem if maxw in m)
    onboard += size
    active += al
    cells = []
    for k in range(0, min(5, maxw - c + 1)):
        cells.append(sum(1 for m in mem if (c + k) in m))
    print(f"26RW{c:02d} | {size:4d} | {al:4d} | " + " ".join(str(x) for x in cells))
print("TOTAL onboarded:", onboard, "active(last):", active, "churned:", onboard - active,
      "retention:", round(100 * active / onboard, 1), "%")

with open("_canvas_data.json", "w", encoding="utf-8") as f:
    f.write(js)
print("wrote _canvas_data.json")
