const path = require("path");
eval(require("fs").readFileSync(path.join(__dirname, "check.js"), "utf8"));
const res = compute();
console.log("cohorts", res.rows.map(r => r.c));
console.log("onboard", res.totals.onboard);
console.log("maxWeek", res.maxWeek);
