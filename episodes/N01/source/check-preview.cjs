const {chromium}=require('playwright');
(async()=>{
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const R=require('path').dirname(__dirname);const p=await browser.newPage({viewport:{width:1400,height:1080}});await p.goto(process.env.PREVIEW_URL||'http://127.0.0.1:8769/%E8%AF%95%E7%9C%8B.html');
await p.waitForFunction(()=>document.querySelector('video').readyState>=1);
console.log(await p.locator('video').evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error})));
await p.locator('[data-time]').nth(2).click();await p.waitForTimeout(1800);
console.log(await p.locator('video').evaluate(v=>({currentTime:v.currentTime,playing:!v.paused,error:v.error})));
await p.screenshot({path:''+R+'/frames/player-check.png'});await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
