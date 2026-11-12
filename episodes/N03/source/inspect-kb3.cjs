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
  
  // 导航到企业知识库
  await page.click('.el-menu-item:has-text("企业知识库")');
  await page.waitForTimeout(3000);
  
  // 点击"文档库"知识库
  console.log('=== 点击"文档库"知识库 ===');
  await page.click('.kb-card-title-main:has-text("文档库")');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-document-detail.png' });
  
  // 获取文件列表
  const content = await page.content();
  
  // 尝试多种选择器获取文件
  const files = await page.$$eval('tr, [class*="file"], [class*="doc"], [class*="item"]', els =>
    els.slice(0, 30).map(e => ({
      text: e.textContent?.trim().substring(0, 120),
      tag: e.tagName,
      class: e.className
    }))
  );
  console.log('页面元素:', JSON.stringify(files.slice(0, 15), null, 2));
  
  // 导航到检索服务
  console.log('\n=== 导航到检索服务 ===');
  await page.click('.el-menu-item:has-text("检索服务")');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-retrieval-test.png' });
  
  // 查看检索服务页面结构
  const retrievalContent = await page.$$eval('input, textarea, button, [class*="search"], [class*="query"]', els =>
    els.slice(0, 20).map(e => ({
      tag: e.tagName,
      type: e.type,
      placeholder: e.placeholder,
      text: e.textContent?.trim().substring(0, 50),
      class: e.className
    }))
  );
  console.log('检索服务元素:', JSON.stringify(retrievalContent, null, 2));
  
  await browser.close();
})();
