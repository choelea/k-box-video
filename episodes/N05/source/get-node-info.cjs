/**
 * 获取BMS2026-B08节点的详细信息
 */
const { chromium } = require('playwright');

const BASE_URL = 'http://47.94.214.243:32121';
const USERNAME = 'zhangqyu';
const PASSWORD = '5MZXF$$uun';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--start-maximized'] });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  // 登录
  console.log('登录中...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle', timeout: 60000 });
  await sleep(1500);

  const inputs = await page.$$('input');
  for (const input of inputs) {
    const type = await input.getAttribute('type');
    if (type === 'text') await input.fill(USERNAME);
    else if (type === 'password') await input.fill(PASSWORD);
  }

  await page.click('button:has-text("下一步")');
  await sleep(3000);

  // 选择租户
  const kbox = await page.$('text=知识平台研发团队KBOX');
  if (kbox) {
    await kbox.click();
    await sleep(3000);
  }

  // 进入企业知识库 → 图谱库 → 新能源汽车归档
  await page.click('text=企业知识库');
  await sleep(1500);
  await page.click('text=图谱库');
  await sleep(2000);
  await page.click('text=新能源汽车归档');
  await sleep(3000);

  console.log('已进入新能源汽车归档');
  console.log('当前URL:', page.url());

  // 切换到图谱tab
  const graphTab = await page.$('text=图谱');
  if (graphTab) {
    await graphTab.click();
    await sleep(5000); // 等待图谱加载
    console.log('已切换到图谱tab');
  }

  // 截取图谱页面
  await page.screenshot({ path: 'temp/graph-page.png' });
  console.log('截图: graph-page.png');

  // 查找BMS2026-B08节点
  console.log('\n查找BMS2026-B08节点...');

  // 尝试通过文本查找
  let node = await page.$('text=BMS2026-B08');
  if (!node) node = await page.$('text=BMS2026');
  if (!node) node = await page.$('[title*="BMS"]');

  if (node) {
    console.log('找到BMS2026-B08节点！');
    await node.click();
    await sleep(3000);

    // 截取点击后的页面
    await page.screenshot({ path: 'temp/node-detail.png' });
    console.log('截图: node-detail.png');

    // 获取节点详情信息
    const detailInfo = await page.$$eval('.node-detail, .detail-panel, [class*="detail"], [class*="panel"], [class*="info"]', els =>
      els.map(e => ({ text: e.textContent?.trim().substring(0, 200), class: e.className?.substring(0, 50) }))
    );
    console.log('\n节点详情:', JSON.stringify(detailInfo, null, 2));

    // 获取所有可见文本中包含关系信息的元素
    const relations = await page.$$eval('*', els =>
      els.filter(e => {
        const text = e.textContent?.trim();
        return text && (text.includes('BMS') || text.includes('关联') || text.includes('关系') ||
                text.includes('供应商') || text.includes('产品') || text.includes('部件'));
      }).slice(0, 30).map(e => e.textContent?.trim().substring(0, 100))
    );
    console.log('\n相关文本:', JSON.stringify(relations.filter(r => r && r.length > 5), null, 2));
  } else {
    console.log('未找到BMS2026-B08节点，尝试在图谱canvas中查找...');

    // 图谱可能使用canvas渲染，尝试点击中间区域
    const canvas = await page.$('canvas');
    if (canvas) {
      const box = await canvas.boundingBox();
      if (box) {
        console.log(`Canvas位置: ${box.x}, ${box.y}, ${box.width}x${box.height}`);
        // 尝试点击canvas中的不同位置
        await page.mouse.click(box.x + box.width * 0.3, box.y + box.height * 0.4);
        await sleep(2000);
        await page.screenshot({ path: 'temp/canvas-click1.png' });

        await page.mouse.click(box.x + box.width * 0.5, box.y + box.height * 0.5);
        await sleep(2000);
        await page.screenshot({ path: 'temp/canvas-click2.png' });

        await page.mouse.click(box.x + box.width * 0.7, box.y + box.height * 0.4);
        await sleep(2000);
        await page.screenshot({ path: 'temp/canvas-click3.png' });
      }
    }

    // 打印页面所有内容用于调试
    const allText = await page.$$eval('*', els =>
      els.filter(e => e.children.length === 0 && e.textContent?.trim())
         .slice(0, 50)
         .map(e => ({ text: e.textContent?.trim().substring(0, 80), tag: e.tagName }))
    );
    console.log('\n页面文本节点:', JSON.stringify(allText, null, 2));
  }

  await sleep(2000);
  await browser.close();
  console.log('\n完成！');
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
