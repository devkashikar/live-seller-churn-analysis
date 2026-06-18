eval(require('fs').readFileSync('_check.js','utf8'));
const res=compute();
console.log('cohorts', res.rows.map(r=>r.c));
console.log('onboard', res.totals.onboard);
console.log('maxWeek', res.maxWeek);
