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
  
  // 获取 token
  const token = await page.evaluate(() => localStorage.getItem('token'));
  const tenantId = await page.evaluate(() => localStorage.getItem('currentTenantId'));
  
  console.log('Token:', token?.substring(0, 50) + '...');
  console.log('Tenant ID:', tenantId);
  
  const question = '供应商来料不良导致的质量问题，应该如何处置？';
  
  // 调用检索 API
  console.log('\n=== 调用检索 API ===');
  console.log('问题:', question);
  
  const result = await page.evaluate(async ({ question, token, tenantId }) => {
    try {
      const response = await fetch('/api/tenant/kb/retrieval-endpoints/search', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'x-tenant-id': tenantId,
          'x-language': 'zh_CN'
        },
        body: JSON.stringify({ 
          query: question, 
          code: 'qwmytgjn',
          topK: 5,
          scoreThreshold: 0.3
        })
      });
      if (response.ok) {
        return await response.json();
      }
      return { error: response.status, text: await response.text() };
    } catch (e) {
      return { error: e.message };
    }
  }, { question, token, tenantId });
  
  console.log('\n=== 检索结果 ===');
  console.log(JSON.stringify(result, null, 2));
  
  await browser.close();
})();
