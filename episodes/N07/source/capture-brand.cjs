// N07 品牌帧截图：从 brand-with-logo.html 生成 8 个场景的截图
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SCENES = ['intro', 'why', 'api', 'mcp', 'skill', 'compare', 'demo', 'outro'];
const HTML = path.resolve(__dirname, 'brand-with-logo.html');
const OUT = path.resolve(__dirname, '..', 'frames');

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  fs.mkdirSync(OUT, { recursive: true });

  for (const scene of SCENES) {
    await page.goto('file:///' + HTML.replace(/\\/g, '/') + '#' + scene);
    await page.waitForFunction(() => window.ready === true, { timeout: 5000 });
    await page.screenshot({ path: path.join(OUT, `brand-${scene}.png`), type: 'png' });
    console.log(`Captured: brand-${scene}.png`);
  }

  await browser.close();
})();
