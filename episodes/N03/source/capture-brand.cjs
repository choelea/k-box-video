const {chromium}=require('playwright'),fs=require('fs'),path=require('path');
const R=path.dirname(__dirname);
const delay=ms=>new Promise(r=>setTimeout(r,ms));

(async()=>{
  const b=await chromium.launch({headless:true});
  const c=await b.newContext({viewport:{width:1920,height:1080}});
  const p=await c.newPage();

  // 包含四个介绍页面
  const slides=['intro','overview','document-intro','wiki-intro','graph-intro','insight-intro','comparison','outro'];

  // 使用带 SVG logo 的品牌页面
  for(const slide of slides){
    await p.goto('file://'+R+'/source/brand-with-logo.html#'+slide,{waitUntil:'networkidle'});
    await delay(500);
    await p.screenshot({path:R+'/frames/brand-'+slide+'.png'});
    console.log('captured',slide);
  }

  await b.close();
  console.log('all brand slides captured');
})().catch(e=>{console.error(e);process.exit(1)});
