const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const ROOT=path.dirname(__dirname),timeline=JSON.parse(fs.readFileSync(path.join(ROOT,'source/timeline.json')));
const overlayCSS=`
html {scroll-behavior:smooth!important} body {zoom:1.25} .marketing-topic{min-height:calc(80dvh - 139px)!important} .marketing-site{min-height:80dvh!important}
::-webkit-scrollbar{width:0!important} * {caret-color:transparent!important}
#film {position:fixed;inset:0;z-index:2147483600;pointer-events:none;zoom:1;font-family:'PingFang SC',sans-serif;color:#fff}
#film .shade {position:absolute;bottom:0;left:0;right:0;height:220px;background:linear-gradient(transparent,rgba(6,10,19,.93) 70%,#060a13)}
#film .chapter {position:absolute;left:66px;bottom:127px;display:flex;gap:20px;align-items:center;transition:opacity .4s}
#film .number {font-size:43px;font-weight:650;color:#f5bf22;line-height:1;border-right:2px solid #f5bf22;padding-right:20px}
#film .ctitle {font-size:29px;font-weight:650;line-height:1.3} #film .kicker{font-size:17px;color:#aeb8ca;margin-top:5px;letter-spacing:1px}
#film .brand {position:absolute;right:64px;bottom:142px;font-size:17px;color:#aeb8ca;letter-spacing:2px}
#film .bar {position:absolute;bottom:0;left:0;height:4px;background:#f5bf22;width:0}
#film .focus{position:absolute;border:3px solid #f5bf22;border-radius:14px;box-shadow:0 0 0 5px #f5bf221c,0 0 30px #f5bf2222;transition:all .65s cubic-bezier(.22,.8,.3,1);opacity:0}
#film .cursor {position:absolute;width:17px;height:17px;background:#f5bf22;border:3px solid #fff;border-radius:50%;box-shadow:0 0 0 9px #f5bf2227;transition:all .65s;opacity:0}
#film .cover {position:absolute;inset:0;background:radial-gradient(ellipse at 80% 20%,#243a5a8c,transparent 60%),linear-gradient(110deg,#070b15fa,#0b1120ee);display:flex;flex-direction:column;justify-content:center;padding:0 156px;transition:opacity .65s;opacity:0}
#film .cover .tag {color:#f5bf22;letter-spacing:5px;font-size:21px;margin-bottom:26px}
#film .cover h1 {font-size:82px;line-height:1.3;margin:0;font-weight:650;letter-spacing:3px}
#film .cover h1 em {font-style:normal;color:#f5bf22}
#film .cover p {font-size:29px;color:#b9c3d7;margin:24px 0 48px}
#film .cover .topics {display:flex;gap:13px;flex-wrap:wrap} #film .cover .topics span {padding:14px 22px;border:1px solid #374057;border-radius:8px;font-size:20px;color:#dce3ee}
#film .cover .url{position:absolute;left:156px;bottom:160px;font-size:20px;letter-spacing:2px;color:#78869e}
#film .cover .line{width:85px;height:5px;background:#f5bf22;margin-bottom:32px}
`;
function initOverlay(){
 document.querySelector('#film')?.remove();
 let style=document.createElement('style');style.textContent=window.__filmCSS;document.head.append(style);
 let el=document.createElement('div');el.id='film';el.innerHTML=`<div class="focus"></div><div class="cursor"></div><div class="shade"></div><div class="chapter"><div class="number"></div><div><div class="ctitle"></div><div class="kicker"></div></div></div><div class="brand">问学知识平台 / 基础介绍</div><div class="cover"><div class="line"></div><div class="tag"></div><h1></h1><p></p><div class="topics"></div><div class="url">kbox.dcsmartvision.com/wiki</div></div><div class="bar"></div>`;document.documentElement.append(el);
}
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 const context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1,recordVideo:{dir:path.join(ROOT,'build'),size:{width:1920,height:1080}}});
 const page=await context.newPage();
 const video=page.video();
 // Warm the actual public pages to avoid loading interruptions during the take.
 for(const slug of ['capabilities','consumption','scenarios','enterprise','docs','positioning']){
  await page.goto('https://kbox.dcsmartvision.com/wiki/'+slug,{waitUntil:'networkidle'});
 }
 await page.evaluate(css=>window.__filmCSS=css,overlayCSS);await page.evaluate(initOverlay);
 await page.mouse.move(1880,1000);
 const delay=ms=>new Promise(r=>setTimeout(r,Math.max(ms,0)));
 const zero=Date.now();const events=[];
 async function at(sec){await delay(sec*1000-(Date.now()-zero));}
 async function scene(chapter,index){
  if(!['intro','outro','positioning'].includes(chapter.id)){
   // Navigation takes place during the preceding sentence's trailing silence.
   await page.goto('https://kbox.dcsmartvision.com/wiki/'+chapter.slug,{waitUntil:'domcontentloaded'});
   await page.evaluate(css=>window.__filmCSS=css,overlayCSS);await page.evaluate(initOverlay);
  }
  if(chapter.id==='outro'){
   await page.evaluate(()=>window.scrollTo({top:0,behavior:'instant'}));
  }
  await page.evaluate(({c,n,d})=>{
   let f=document.querySelector('#film');f.querySelector('.number').textContent=String(n).padStart(2,'0');f.querySelector('.ctitle').textContent=c.title;f.querySelector('.kicker').textContent=c.kicker;
   f.querySelector('.focus').style.opacity=0;f.querySelector('.cursor').style.opacity=0;
   const cover=f.querySelector('.cover'),isCover=['intro','outro'].includes(c.id);cover.style.opacity=isCover?1:0;
   f.querySelector('.chapter').style.opacity=isCover?0:1;f.querySelector('.brand').style.opacity=isCover?0:1;
   if(isCover){
    cover.querySelector('.tag').textContent=c.id==='intro'?'K-BOX · 产品导览':'K-BOX · 企业知识就绪层';
    cover.querySelector('h1').innerHTML=c.id==='intro'?'问学<em>知识平台</em>':'让企业知识<br>成为<em>可信上下文</em>';
    cover.querySelector('p').textContent=c.id==='intro'?'企业知识的治理、服务与可信供给':'从知识治理出发，连接智能体与业务应用';
    cover.querySelector('.topics').innerHTML=(c.id==='intro'?['产品定位','产品能力','知识消费','应用场景','企业保障','开发者文档']:['统一知识治理','双知识服务引擎','统一可信供给']).map(t=>'<span>'+t+'</span>').join('');
   }
   // Resume progress across document navigations.
   let bar=f.querySelector('.bar');bar.style.width=(c.start/d*100)+'%';
   bar.animate([{width:(c.start/d*100)+'%'},{width:(c.end/d*100)+'%'}],{duration:(c.end-c.start)*1000,fill:'forwards',easing:'linear'});
  },{c:chapter,n:Math.min(Math.max(index,1),6),d:timeline.duration});
  events.push({type:'chapter',id:chapter.id,time:(Date.now()-zero)/1000});console.log('recording',chapter.id,(Date.now()-zero)/1000);
 }
 async function focus(selector){
  await page.evaluate(sel=>{
   const target=sel?document.querySelector(sel):null,f=document.querySelector('#film');
   if(!target){f.querySelector('.focus').style.opacity=0;f.querySelector('.cursor').style.opacity=0;return}
   const r=target.getBoundingClientRect();const b=f.querySelector('.focus');Object.assign(b.style,{left:(r.left-6)+'px',top:(r.top-6)+'px',width:(r.width+12)+'px',height:(r.height+12)+'px',opacity:1});
   Object.assign(f.querySelector('.cursor').style,{left:(r.right-20)+'px',top:(r.top-15)+'px',opacity:1});
  },selector);
 }
 async function scrollToSelector(selector){
  await focus(null);await page.evaluate(sel=>{const el=document.querySelector(sel);if(el)window.scrollTo({top:el.getBoundingClientRect().top+scrollY-125,behavior:'smooth'})},selector);await delay(950);
 }
 const focusSelectors={
 positioning:['.architecture-core-row','.architecture-source-row','.architecture-app-row','.architecture-core-row'],
 capabilities:[null,'.asset-card:nth-child(1)','.asset-card:nth-child(2)','.asset-card:nth-child(3)','.asset-card:nth-child(4)','.pillar-grid'],
 consumption:[null,'.consumption-path:nth-child(1)','.consumption-path:nth-child(2)','.consumption-path:nth-child(3)'],
 scenarios:[null,'.scenario-card:nth-child(1)','.scenario-card:nth-child(2)','.scenario-card:nth-child(3)','.scenario-card:nth-child(4)'],
 enterprise:[null,'.enterprise-list > div:nth-child(1)','.enterprise-list > div:nth-child(2)','.enterprise-list > div:nth-child(3)','.enterprise-list > div:nth-child(4)']};
 await scene(timeline.chapters[0],0);
 await page.screenshot({path:path.join(ROOT,'frames/cover.png')});
 for(let ci=0;ci<timeline.chapters.length;ci++){
  const c=timeline.chapters[ci];
  if(ci){await at(c.start-.12);await scene(c,ci);}
  for(let li=0;li<c.segments.length;li++){
   const s=c.segments[li];await at(s.start+.1);
   if(focusSelectors[c.id])await focus(focusSelectors[c.id][li]);
   if(c.id==='docs'){
    if(li===1){await scrollToSelector('#quick-start');await focus('.docs-choice');}
    if(li===2){
     await scrollToSelector('#product-guides');await delay(1250);
     await scrollToSelector('#api-reference');await delay(1250);
     await scrollToSelector('#deployment');
    }
    if(li===3){await scrollToSelector('#quick-start .quick-start-grid');await focus('.quick-start-card:nth-child(2)');}
   }
   if(li===1||c.id==='positioning'&&li===0)await page.screenshot({path:path.join(ROOT,'frames',c.id+'-recorded.png')});
  }
 }
 await at(timeline.duration+.4);
 const elapsed=(Date.now()-zero)/1000;
 await page.close();
 const videoPath=await video.path();
 await context.close();await browser.close();
 fs.writeFileSync(path.join(ROOT,'source/recording.json'),JSON.stringify({videoPath,elapsed,events},null,2));console.log('done',videoPath,elapsed);
})().catch(e=>{console.error(e);process.exit(1)});
