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
  
  console.log('=== 知识库列表 ===');
  
  // 获取知识库列表
  const libs = await page.$$eval('[class*="card"], [class*="item"], .knowledge-list > div', els => 
    els.slice(0, 20).map(e => ({
      text: e.textContent?.trim().substring(0, 100),
      class: e.className
    }))
  );
  console.log(JSON.stringify(libs, null, 2));
  
  // 尝试点击第一个知识库
  try {
    const firstLib = page.locator('[class*="card"], [class*="item"]').first();
    if (await firstLib.isVisible({ timeout: 3000 })) {
      await firstLib.click();
      await page.waitForTimeout(3000);
      
      console.log('\n=== 知识库详情 ===');
      console.log('URL:', page.url());
      
      // 获取文件列表
      const files = await page.$$eval('table tr, [class*="file"], [class*="document"]', els =>
        els.slice(0, 15).map(e => ({
          text: e.textContent?.trim().substring(0, 100),
          class: e.className
        }))
      );
      console.log(JSON.stringify(files, null, 2));
    }
  } catch (e) {
    console.log('Cannot click first library:', e.message);
  }
  
  await browser.close();
})();
