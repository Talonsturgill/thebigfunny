// prove the two acting helpers build sane tracks from real cue shapes
function watchSpeaker(cues, me, otherSide, amount=0.34){
  const out=[{t:0,v:0}];
  for(const c of cues) out.push({t:Math.max(0,c.start-0.18),
    v: c.who===me ? 0.06*otherSide : amount*otherSide});
  return out;
}
function gestureOnLines(cues, me, tell, hold='stand'){
  const out=[{t:0,pose:hold}];
  for(const c of cues){
    if(c.who!==me) continue;
    if(c.end-c.start<0.7) continue;
    out.push({t:Math.max(0,c.start-0.12),pose:tell});
    out.push({t:c.end+0.10,pose:hold});
  }
  return out;
}
const cues=[{start:0.6,end:2.0,who:'DEE'},{start:2.6,end:3.0,who:'RAY'},
            {start:4.6,end:6.6,who:'DEE'},{start:7.4,end:11.3,who:'RAY'}];
let ok=true;
const w=watchSpeaker(cues,'RAY',-1);
// Ray faces front-ish on his own lines, turns toward Dee on hers
const rayOwn=w.filter((k,i)=>i>0&&[2,4].includes(i)).every(k=>Math.abs(k.v)<0.1);
const rayOther=[w[1],w[3]].every(k=>Math.abs(k.v)>0.3);
console.log(`  ${rayOwn?'ok  ':'FAIL'} Ray faces out on his OWN lines`);
console.log(`  ${rayOther?'ok  ':'FAIL'} Ray turns toward Dee on HERS`);
ok&&=rayOwn&&rayOther;
// anticipation: every key lands BEFORE its line
const antic=w.slice(1).every((k,i)=>k.t<=cues[i].start);
console.log(`  ${antic?'ok  ':'FAIL'} every turn ANTICIPATES its line`);
ok&&=antic;
// gesture: only Ray's lines, only ones long enough to read
const g=gestureOnLines(cues,'RAY','point');
const short=g.some(k=>Math.abs(k.t-2.48)<0.01);
const long=g.some(k=>Math.abs(k.t-7.28)<0.01);
console.log(`  ${!short?'ok  ':'FAIL'} the 0.4s line is too short to gesture on, skipped`);
console.log(`  ${long?'ok  ':'FAIL'} the 3.9s line gets a gesture`);
ok&&=!short&&long;
// every gesture returns to rest
const ret=g.filter(k=>k.pose==='point').length===g.filter(k=>k.pose==='stand').length-1+1-1+1;
const pts=g.filter(k=>k.pose==='point').length, stands=g.filter(k=>k.pose==='stand').length;
const balanced = stands === pts + 1;   // initial hold + one release per gesture
console.log(`  ${balanced?'ok  ':'FAIL'} every gesture releases back to rest (${pts} out, ${stands} rest)`);
ok&&=balanced;
console.log(ok?"\nmannerisms: correct":"\nmannerisms: BROKEN");
process.exit(ok?0:1);
