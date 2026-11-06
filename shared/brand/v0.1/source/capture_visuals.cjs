const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const {pathToFileURL}=require('url');
const R=path.dirname(__dirname);
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 const results=[];
 for(const scene of ['opening','concept','ui','ending']){
  await page.goto(pathToFileURL(path.join(R,'visual/template.html')).href+'#'+scene);
  await page.waitForFunction(()=>window.ready===true);
  await page.evaluate(async()=>{await Promise.all(Array.from(document.images).map(i=>i.decode()))});
  const overflow=await page.evaluate(()=>Array.from(document.querySelectorAll('h1,h2,.card,.ui,.next')).filter(e=>{const r=e.getBoundingClientRect();return r.x<0||r.y<0||r.right>1920||r.bottom>1010}).map(e=>e.className||e.tagName));
  if(overflow.length)throw new Error('Overflow '+scene+': '+overflow.join(','));
  await page.screenshot({path:path.join(R,'visual/frames',scene+'.png')});
  results.push({scene,viewport:[1920,1080],imagesLoaded:true,overflow:[]});
 }
 fs.writeFileSync(path.join(R,'review/visual-verification.json'),JSON.stringify(results,null,2));
 await browser.close();console.log(JSON.stringify(results));
})().catch(e=>{console.error(e);process.exit(1)});
