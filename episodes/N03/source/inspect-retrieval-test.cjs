const { chromium } = require('playwright');

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
  
  try {
    await page.click('text=知识平台研发团队');
    await page.waitForTimeout(2000);
  } catch (e) {}
  
  // 导航到检索服务
  await page.click('.el-menu-item:has-text("检索服务")');
  await page.waitForTimeout(3000);
  
  // 点击"检索测试"标签
  console.log('=== 点击"检索测试" ===');
  await page.click('text=检索测试');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-retrieval-test-page.png' });
  
  const testPageContent = await page.evaluate(() => document.body.innerText);
  console.log('检索测试页面:\n', testPageContent.substring(0, 5000));
  
  await browser.close();
})();
