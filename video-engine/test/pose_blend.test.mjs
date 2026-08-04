const GESTURE_EASE_S = 0.34;
function poseAt(track, f, fps) {
  if (!track.length) return [{pose:'stand', w:1}];
  const t = f/fps;
  const ks = [...track].sort((a,b)=>a.t-b.t);
  let i = 0;
  while (i+1 < ks.length && t >= ks[i+1].t + (ks[i+1].ease ?? GESTURE_EASE_S)) i++;
  const cur = ks[i], nxt = ks[i+1];
  if (!nxt) return [{pose:cur.pose, w:1}];
  const dur = Math.max(1e-3, nxt.ease ?? GESTURE_EASE_S);
  if (t < nxt.t) return [{pose:cur.pose, w:1}];
  const u = Math.min(1,(t-nxt.t)/dur);
  const e = u*u*(3-2*u);
  if (e<=0) return [{pose:cur.pose, w:1}];
  if (e>=1) return [{pose:nxt.pose, w:1}];
  return [{pose:cur.pose, w:1-e},{pose:nxt.pose, w:e}];
}
const track = [{t:0, pose:'arms-crossed'}, {t:2.0, pose:'point'}, {t:5.0, pose:'stand'}];
const show = f => { const m = poseAt(track,f,30);
  return m.map(x=>`${x.pose}:${x.w.toFixed(2)}`).join(' + '); };
let ok = true;
const cases = [
  [0,   'arms-crossed:1.00', 'before any transition, holds'],
  [30,  'arms-crossed:1.00', 'still holding at 1.0s'],
  [59,  'arms-crossed:1.00', 'one frame before the key'],
  [60,  'arms-crossed:1.00', 'exactly on the key, blend starts at 0'],
  [65,  null,                'mid-gesture: BOTH poses present'],
  [71,  'point:1.00',        'gesture complete after 0.34s'],
  [150, 'point:1.00',        'exactly on a later key: previous pose, blend about to start'],
  [155, null,                'mid second gesture: BOTH poses present'],
  [161, 'stand:1.00',        'second gesture complete'],
];
for (const [f, want, why] of cases) {
  const got = show(f);
  const m = poseAt(track,f,30);
  let pass;
  if (want === null) { pass = m.length===2 && m[0].w>0 && m[1].w>0; }
  else pass = got === want;
  if (!pass) ok = false;
  console.log(`  ${pass?'ok  ':'FAIL'} f=${String(f).padStart(3)}  ${got.padEnd(34)} ${why}`);
}
// weights always sum to 1
for (let f=0; f<180; f++){
  const sum = poseAt(track,f,30).reduce((a,x)=>a+x.w,0);
  if (Math.abs(sum-1)>1e-9){ console.log(`  FAIL weights sum to ${sum} at f=${f}`); ok=false; break; }
}
console.log(ok ? "\n  ok   weights sum to 1 across the whole track\n\nposeAt: correct"
               : "\nposeAt: BROKEN");
process.exit(ok?0:1);
