// Record public pages only. No authentication or generated answers.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const R=path.dirname(__dirname),T=JSON.parse(fs.readFileSync(path.join(R,'source/timeline.json')));
const pause=ms=>new Promise(r=>setTimeout(r,Math.max(0,ms)));
const selectors={positioning:['.architecture-core-row','.architecture-source-row','.architecture-app-row','.architecture-core-row'],capabilities:[null,'.asset-card:nth-child(1)','.asset-card:nth-child(2)','.asset-card:nth-child(3)','.asset-card:nth-child(4)','.pillar-grid'],consumption:[null,'.consumption-path:nth-child(1)','.consumption-path:nth-child(2)','.consumption-path:nth-child(3)'],scenarios:[null,'.scenario-card:nth-child(1)','.scenario-card:nth-child(2)','.scenario-card:nth-child(3)','.scenario-card:nth-child(4)'],enterprise:[null,'.enterprise-list > div:nth-child(1)','.enterprise-list > div:nth-child(2)','.enterprise-list > div:nth-child(3)','.enterprise-list > div:nth-child(4)']};
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});const records=process.env.ONLY_SCENE?JSON.parse(fs.readFileSync(path.join(R,'source/scene-recordings.json'))).filter(r=>r.id!==process.env.ONLY_SCENE):[];
 for(const c of T.chapters.filter(c=>!['intro','outro'].includes(c.id)&&(!process.env.ONLY_SCENE||c.id===process.env.ONLY_SCENE))){
  const ctx=await browser.newContext({viewport:{width:1760,height:880},deviceScaleFactor:1,recordVideo:{dir:path.join(R,'assets/recordings'),size:{width:1760,height:880}}});const p=await ctx.newPage();
  await p.goto('https://kbox.dcsmartvision.com/wiki/'+(c.id==='docs'?'enterprise':c.slug),{waitUntil:'networkidle'});
  if(c.id==='docs'){await p.getByRole('link',{name:'文档中心',exact:true}).first().click();await p.waitForURL('**/wiki/docs');await p.getByRole('heading',{name:'文档中心',exact:true}).waitFor({state:'visible'});await p.waitForLoadState('networkidle');}
  await p.addStyleTag({content:`body{zoom:1.2} .marketing-topic{min-height:calc(83.333dvh - 115px)!important}.marketing-site{min-height:83.333dvh!important} ::-webkit-scrollbar{width:0} *{caret-color:transparent!important} [data-film-focus]{outline:2px solid #f2c34e!important;outline-offset:5px;border-radius:9px}`});
  await p.evaluate(()=>document.fonts.ready);await p.mouse.move(1740,860);const video=p.video();const zero=Date.now(),events=[];
  async function at(t){await pause(t*1000-(Date.now()-zero))}
  async function focus(sel){if(!sel)return;const item=p.locator(sel);if(!await item.count())throw Error('Missing target: '+sel);await p.evaluate(s=>{document.querySelectorAll('[data-film-focus]').forEach(e=>e.removeAttribute('data-film-focus'));document.querySelector(s).setAttribute('data-film-focus','')},sel);events.push({type:'focus',selector:sel,time:(Date.now()-zero)/1000});}
  async function scroll(sel){const e=p.locator(sel).first();if(!await e.count())throw Error('Missing docs target '+sel);await p.evaluate(s=>{document.querySelectorAll('[data-film-focus]').forEach(e=>e.removeAttribute('data-film-focus'));const e=document.querySelector(s);window.scrollTo({top:e.getBoundingClientRect().top+scrollY-100,behavior:'instant'})},sel);events.push({type:'scroll',selector:sel,time:(Date.now()-zero)/1000});await pause(250)}
  for(let li=0;li<c.segments.length;li++){
   const s=c.segments[li];await at(s.start-c.start+.08);
   if(c.id==='docs'){
    if(li===1){await scroll('#quick-start');await focus('.docs-choice');}
    if(li===2){await scroll('#product-guides');await at(s.start-c.start+2.9);await scroll('#api-reference');await at(s.start-c.start+5.3);await scroll('#deployment');}
    if(li===3){await scroll('.quick-start-grid');await focus('.quick-start-card:nth-child(2)');}
   }else await focus(selectors[c.id][li]);
   await p.screenshot({path:path.join(R,'frames',`v2-${c.id}-${li}.png`)});
  }
  await at(c.end-c.start+.15);const elapsed=(Date.now()-zero)/1000;await p.close();const raw=await video.path();await ctx.close();
  records.push({id:c.id,videoPath:path.relative(R,raw),elapsed,chapter_duration:c.end-c.start,events,captured_on:'2026-11-03',source:'https://kbox.dcsmartvision.com/wiki/'+c.slug});fs.writeFileSync(path.join(R,'source/scene-recordings.json'),JSON.stringify(records,null,2));console.log('recorded',c.id,elapsed);
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
