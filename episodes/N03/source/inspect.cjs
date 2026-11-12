const { chromium }=require('playwright');
const fs=require('fs');
const path=require('path');
const root=path.dirname(__dirname);
(async()=>{
 fs.mkdirSync(path.join(root,'source/snapshots'),{recursive:true});fs.mkdirSync(path.join(root,'frames/snapshots'),{recursive:true});
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 for (const slug of ['positioning','capabilities','consumption','scenarios','enterprise','docs']){
 await page.goto(`https://kbox.dcsmartvision.com/wiki/${slug}`,{waitUntil:'networkidle'});
 await page.screenshot({path:path.join(root,'frames/snapshots',slug+'.png')});
 const data=await page.evaluate(()=>({title:document.title,text:document.body.innerText,height:document.body.scrollHeight,headings:[...document.querySelectorAll('h1,h2,h3')].map(x=>({text:x.innerText,y:x.getBoundingClientRect().top+scrollY}))}));
 fs.writeFileSync(path.join(root,'source/snapshots',slug+'.json'),JSON.stringify(data,null,2));
 console.log(slug,JSON.stringify(data));
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
