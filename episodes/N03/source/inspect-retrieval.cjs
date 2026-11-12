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
  console.log('=== 导航到检索服务 ===');
  await page.click('.el-menu-item:has-text("检索服务")');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-retrieval-list.png' });
  
  // 获取检索服务列表
  const services = await page.evaluate(() => document.body.innerText);
  console.log('检索服务:\n', services.substring(0, 3000));
  
  // 尝试点击第一个检索服务进入测试
  console.log('\n=== 尝试进入检索测试 ===');
  
  // 查找"测试"或"调试"按钮
  const testBtns = await page.$$eval('button, .el-button', els =>
    els.filter(e => e.textContent?.includes('测试') || e.textContent?.includes('调试'))
      .map(e => ({ text: e.textContent?.trim(), class: e.className }))
  );
  console.log('测试按钮:', JSON.stringify(testBtns, null, 2));
  
  // 尝试点击检索服务行
  await page.locator('tr:has-text("whpn"), tr:has-text("默认"), .doc-query-body tr').first().click();
  await page.waitForTimeout(3000);
  
  console.log('URL after click:', page.url());
  await page.screenshot({ path: 'frames/v3-retrieval-test.png' });
  
  const testContent = await page.evaluate(() => document.body.innerText);
  console.log('测试页面:\n', testContent.substring(0, 4000));
  
  await browser.close();
})();
