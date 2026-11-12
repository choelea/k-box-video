const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // 监听网络请求
  const apiCalls = [];
  page.on('request', request => {
    if (request.url().includes('/api/') || request.url().includes('retrieval')) {
      apiCalls.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers()
      });
    }
  });
  
  // 登录
  await page.goto('http://47.94.214.243:32121/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await page.fill('input[placeholder*="邮箱/手机号/用户代码"]', 'zhangqyu');
  await page.fill('input[placeholder*="密码"]', '5MZXF$$uun');
  await page.click('button:has-text("下一步")');
  await page.waitForTimeout(5000);
  
  try {
    await page.click('text=知识平台研发团队');
    await page.waitForTimeout(2000);
  } catch (e) {}
  
  // 导航到检索服务页面
  await page.click('.el-menu-item:has-text("检索服务")');
  await page.waitForTimeout(3000);
  
  // 打印捕获的 API 调用
  console.log('=== 捕获的 API 调用 ===');
  console.log(JSON.stringify(apiCalls.slice(0, 10), null, 2));
  
  // 获取 localStorage
  const storage = await page.evaluate(() => {
    const items = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      items[key] = localStorage.getItem(key);
    }
    return items;
  });
  console.log('\n=== localStorage ===');
  console.log(JSON.stringify(storage, null, 2));
  
  await browser.close();
})();
