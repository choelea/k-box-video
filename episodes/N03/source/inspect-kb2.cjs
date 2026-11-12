const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // 登录
  await page.goto('http://47.94.214.243:32121/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await page.fill('input[placeholder*="邮箱/手机号/用户代码"]', 'zhangqyu');
  await page.fill('input[placeholder*="密码"]', '5MZXF$$uun');
  await page.click('button:has-text("下一步")');
  await page.waitForTimeout(3000);
  
  // 选择租户
  try {
    await page.click('text=知识平台研发团队');
    await page.waitForTimeout(2000);
  } catch (e) {}
  
  // 导航到企业知识库
  await page.click('.el-menu-item:has-text("企业知识库")');
  await page.waitForTimeout(3000);
  
  console.log('=== 知识库卡片列表 ===');
  
  // 获取所有知识库卡片
  const cards = await page.$$eval('.kb-card', els =>
    els.map(e => ({
      name: e.querySelector('.kb-card-title-main')?.textContent?.trim() || '',
      desc: e.querySelector('.kb-card-desc')?.textContent?.trim() || '',
      type: e.querySelector('.kb-card-type')?.textContent?.trim() || '',
      count: e.querySelector('.kb-card-count')?.textContent?.trim() || ''
    }))
  );
  console.log(JSON.stringify(cards, null, 2));
  
  // 点击第一个知识库进入详情
  try {
    const firstCard = page.locator('.kb-card').first();
    const firstName = await firstCard.querySelector('.kb-card-title-main')?.textContent?.trim();
    console.log('\n点击知识库:', firstName);
    await firstCard.click();
    await page.waitForTimeout(3000);
    
    console.log('\n=== 知识库详情页 ===');
    console.log('URL:', page.url());
    
    // 截图
    await page.screenshot({ path: 'frames/v3-document-detail.png' });
    
    // 获取文件列表
    const files = await page.$$eval('.file-item, .doc-item, table tbody tr', els =>
      els.slice(0, 20).map(e => ({
        name: e.querySelector('.file-name, .doc-name, td:first-child')?.textContent?.trim() || e.textContent?.trim().substring(0, 80),
        status: e.querySelector('.file-status, .doc-status')?.textContent?.trim() || ''
      }))
    );
    console.log('文件列表:', JSON.stringify(files, null, 2));
    
  } catch (e) {
    console.log('Error:', e.message);
  }
  
  await browser.close();
})();
