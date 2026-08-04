// prove resample preserves endpoints, spaces by arc length, and blends sanely
function resample(pts, n) {
  if (n < 2) return pts.slice(0, Math.max(1, n));
  if (pts.length === 0) return [];
  if (pts.length === 1) return Array.from({length: n}, () => pts[0]);
  const seg = []; let total = 0;
  for (let i = 1; i < pts.length; i++) {
    const d = Math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1]);
    seg.push(d); total += d;
  }
  if (total <= 1e-9) return Array.from({length: n}, () => pts[0]);
  const out = [pts[0]]; const step = total/(n-1);
  let i = 1, walked = 0;
  for (let k = 1; k < n-1; k++) {
    const target = k*step;
    while (i < seg.length && walked + seg[i-1] < target) { walked += seg[i-1]; i++; }
    const rem = target - walked;
    const t = seg[i-1] > 1e-9 ? rem/seg[i-1] : 0;
    out.push([pts[i-1][0]+(pts[i][0]-pts[i-1][0])*t, pts[i-1][1]+(pts[i][1]-pts[i-1][1])*t]);
  }
  out.push(pts[pts.length-1]);
  return out;
}
const near=(a,b,e=1e-6)=>Math.abs(a-b)<e;
let ok = true;
// 1. straight line, unevenly sampled -> evenly spaced
const line = [[0,0],[1,0],[10,0]];
const r = resample(line, 6);
const gaps = r.slice(1).map((p,i)=>p[0]-r[i][0]);
const even = gaps.every(g=>near(g, 2.0, 1e-9));
console.log(`  ${even?'ok  ':'FAIL'} uneven input resampled to even arc spacing  ${gaps.map(g=>g.toFixed(2))}`);
ok &&= even;
// 2. endpoints preserved exactly
const ends = near(r[0][0],0) && near(r[5][0],10);
console.log(`  ${ends?'ok  ':'FAIL'} endpoints preserved exactly`);
ok &&= ends;
// 3. different lengths blend, and t=0/t=1 return the originals
const a = [[0,0],[5,5],[10,0]];          // 3 pts
const b = [[0,0],[2,9],[6,9],[10,0]];    // 4 pts
const blend=(A,B,t,n=6)=>{const X=resample(A,n),Y=resample(B,n);
  return X.map((p,i)=>[p[0]+(Y[i][0]-p[0])*t, p[1]+(Y[i][1]-p[1])*t]);};
const at0 = blend(a,b,0), at1 = blend(a,b,1);
const same = JSON.stringify(at0)===JSON.stringify(resample(a,6)) &&
             JSON.stringify(at1)===JSON.stringify(resample(b,6));
console.log(`  ${same?'ok  ':'FAIL'} t=0 and t=1 return the originals (3pt vs 4pt)`);
ok &&= same;
// 4. midpoint is between, never NaN
const mid = blend(a,b,0.5);
const sane = mid.every(p=>Number.isFinite(p[0])&&Number.isFinite(p[1]));
console.log(`  ${sane?'ok  ':'FAIL'} midpoint blend is finite  ${mid.map(p=>'['+p.map(v=>v.toFixed(1))+']').join(' ')}`);
ok &&= sane;
// 5. degenerate input does not divide by zero
const deg = resample([[3,3],[3,3],[3,3]], 5);
const dok = deg.length===5 && deg.every(p=>near(p[0],3)&&near(p[1],3));
console.log(`  ${dok?'ok  ':'FAIL'} degenerate polyline handled, no NaN`);
ok &&= dok;
console.log(ok ? "\nresample: correct" : "\nresample: BROKEN");
process.exit(ok?0:1);
