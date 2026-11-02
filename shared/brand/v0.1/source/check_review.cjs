const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const R=path.dirname(__dirname),URL='http://127.0.0.1:8770/shared/brand/v0.1/'+encodeURIComponent('试看.html');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(URL,{waitUntil:'networkidle'});
 await page.waitForFunction(()=>document.querySelector('video').readyState>=1);
 const metadata=await page.locator('video').evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error}));
 if(Math.abs(metadata.duration-30)>.1||metadata.width!==1920||metadata.height!==1080||metadata.error)throw Error('Invalid video metadata');
 const links=await page.locator('a[href]').evaluateAll(els=>Array.from(new Set(els.map(e=>e.href))));
 for(const link of links){const res=await page.request.get(link,{headers:{Range:'bytes=0-127'}});if(!res.ok())throw Error('Broken link '+link+' '+res.status());}
 const audio=[];
 for(let i=0;i<4;i++){
  const player=page.locator('.card > audio').nth(i);
  await player.scrollIntoViewIfNeeded();
  await player.click({position:{x:25,y:20}});
  await page.waitForTimeout(400);
  const state=await player.evaluate(v=>({duration:v.duration,time:v.currentTime,playing:!v.paused,error:v.error}));
  if(state.error||!state.playing||state.duration<12||state.duration>25)throw Error('Invalid audio '+JSON.stringify(state));
  audio.push(state);await player.evaluate(v=>v.pause());
 }
 const seeks=[];
 for(const i of [0,1,2,3]){
  const b=page.locator('[data-time]').nth(i);await b.click();await page.waitForTimeout(350);
  const state=await page.locator('video').evaluate(v=>({time:v.currentTime,playing:!v.paused,error:v.error}));
  const target=Number(await b.getAttribute('data-time'));
  if(!state.playing||state.error||state.time<target||state.time>target+3)throw Error('Seek failure');
  seeks.push({...state,target});
 }
 await page.locator('video').evaluate(v=>{v.pause();v.currentTime=18});
 await page.waitForTimeout(300);await page.evaluate(()=>scrollTo(0,0));
 await page.screenshot({path:path.join(R,'source/review-desktop.png')});
 await page.setViewportSize({width:390,height:844});await page.waitForTimeout(200);
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 if(overflow)throw Error('Mobile overflow');
 await page.screenshot({path:path.join(R,'source/review-mobile.png')});
 if(errors.length)throw Error(errors.join('\n'));
 const result={metadata,linksChecked:links.length,candidatePlayback:audio,chapterSeeks:seeks,mobileOverflow:false,pageErrors:errors,pronunciationApproval:'pending'};
 fs.writeFileSync(path.join(R,'source/player-verification.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify(result));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
