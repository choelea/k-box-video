/**
 * N04 品牌页面和演示UI截图捕获
 * 使用 Playwright 捕获 HTML 页面截图
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const EPISODE_DIR = path.resolve(__dirname, '..');
const FRAMES_DIR = path.join(EPISODE_DIR, 'frames');

// 确保输出目录存在
if (!fs.existsSync(FRAMES_DIR)) {
  fs.mkdirSync(FRAMES_DIR, { recursive: true });
}

// 品牌页面场景
const BRAND_SCENES = ['intro', 'problem', 'solution', 'demo-overview', 'value', 'comparison', 'outro'];

// 演示UI场景 - 每个场景独立加载
const DEMO_SCENES = [
  { id: 'sources', output: 'demo-sources' },
  { id: 'pages', output: 'demo-pages' },
  { id: 'detail', output: 'demo-detail' },
  { id: 'qa', output: 'demo-qa' }
];

const delay = ms => new Promise(r => setTimeout(r, ms));

async function captureBrandScenes(browser) {
  console.log('捕获品牌页面截图...');
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  const htmlPath = path.join(EPISODE_DIR, 'source', 'brand-with-logo.html');
  const fileUrl = 'file:///' + htmlPath.replace(/\\/g, '/');

  for (const scene of BRAND_SCENES) {
    // 每次都重新加载页面
    await page.goto(`${fileUrl}#${scene}`, { waitUntil: 'networkidle' });
    await delay(800);

    const outputPath = path.join(FRAMES_DIR, `brand-${scene}.png`);
    await page.screenshot({ path: outputPath, type: 'png' });
    console.log(`  ✓ brand-${scene}.png`);
  }

  await context.close();
}

async function captureDemoScenes(browser) {
  console.log('捕获演示UI截图...');

  const htmlPath = path.join(EPISODE_DIR, 'source', 'demo-ui.html');
  const fileUrl = 'file:///' + htmlPath.replace(/\\/g, '/');

  for (const scene of DEMO_SCENES) {
    // 每个场景使用新的context，确保完全重新加载
    const context = await browser.newContext({ viewport: { width: 1760, height: 880 } });
    const page = await context.newPage();

    await page.goto(`${fileUrl}#${scene.id}`, { waitUntil: 'load' });
    await delay(500);

    const outputPath = path.join(FRAMES_DIR, `${scene.output}.png`);
    await page.screenshot({ path: outputPath, type: 'png', fullPage: false });

    const stats = fs.statSync(outputPath);
    console.log(`  ✓ ${scene.output}.png (${(stats.size/1024).toFixed(0)}KB)`);

    await context.close();
  }
}

async function main() {
  console.log('开始截图捕获...\n');

  const browser = await chromium.launch({ headless: true });

  try {
    await captureBrandScenes(browser);
    console.log('');
    await captureDemoScenes(browser);
    console.log('\n截图捕获完成！');
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error('截图失败:', err);
  process.exit(1);
});
