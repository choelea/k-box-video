/**
 * N05 品牌幻灯片截图捕获
 * 使用 Playwright 捕获 HTML 页面截图
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const EPISODE_DIR = path.resolve(__dirname, '..');
const FRAMES_DIR = path.join(EPISODE_DIR, 'frames');

if (!fs.existsSync(FRAMES_DIR)) {
  fs.mkdirSync(FRAMES_DIR, { recursive: true });
}

// N05 品牌页面场景
const BRAND_SCENES = ['intro', 'limits', 'value', 'comparison', 'outro'];

const delay = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  const browser = await chromium.launch();

  console.log('捕获品牌页面截图...');
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  const htmlPath = path.join(EPISODE_DIR, 'source', 'brand-with-logo.html');
  const fileUrl = 'file:///' + htmlPath.replace(/\\/g, '/');

  for (const scene of BRAND_SCENES) {
    await page.goto(`${fileUrl}#${scene}`, { waitUntil: 'networkidle' });
    await delay(1000);

    // 等待字体加载
    await page.evaluate(() => document.fonts.ready);
    await delay(500);

    const outputPath = path.join(FRAMES_DIR, `brand-${scene}.png`);
    await page.screenshot({ path: outputPath, type: 'png' });
    console.log(`  brand-${scene}.png`);
  }

  await context.close();
  await browser.close();
  console.log('\n品牌截图完成！');
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
