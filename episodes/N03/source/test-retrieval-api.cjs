const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // 登录获取 cookie
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
  
  // 获取 cookies
  const cookies = await page.context().cookies();
  const tokenCookie = cookies.find(c => c.name === 'token' || c.name === 'access_token' || c.name.includes('token'));
  console.log('Cookies:', JSON.stringify(cookies.map(c => c.name), null, 2));
  
  // 尝试调用检索 API
  console.log('\n=== 调用检索 API ===');
  
  const question = '供应商来料不良导致的质量问题，应该如何处置？';
  
  // 方法1：直接在页面中调用 API
  const result = await page.evaluate(async (question) => {
    try {
      // 尝试调用检索服务 API
      const response = await fetch('/api/kb/retrieval-endpoints/qwmytgjn/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question, topK: 5 })
      });
      if (response.ok) {
        return await response.json();
      }
      return { error: response.status, text: await response.text() };
    } catch (e) {
      return { error: e.message };
    }
  }, question);
  
  console.log('检索结果:', JSON.stringify(result, null, 2));
  
  // 方法2：尝试其他 API 路径
  console.log('\n=== 尝试其他 API 路径 ===');
  
  const result2 = await page.evaluate(async (question) => {
    const paths = [
      '/api/retrieval/search',
      '/api/kb/search',
      '/api/v1/retrieval/search',
      '/kb/api/search'
    ];
    
    for (const path of paths) {
      try {
        const response = await fetch(path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            query: question, 
            endpointCode: 'qwmytgjn',
            topK: 5 
          })
        });
        if (response.ok) {
          return { path, data: await response.json() };
        }
      } catch (e) {}
    }
    return { error: 'All paths failed' };
  }, question);
  
  console.log('结果:', JSON.stringify(result2, null, 2));
  
  await browser.close();
})();
