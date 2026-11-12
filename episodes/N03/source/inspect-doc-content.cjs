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
  
  // 直接访问售后知识库
  await page.goto('http://47.94.214.243:32121/kb/761', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);
  
  // 点击第一个文档查看详情
  console.log('=== 查看文档详情 ===');
  
  // 尝试点击文档名称
  await page.click('text=星途新能源售后质量处置指引');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-doc-content-1.png' });
  
  const content = await page.evaluate(() => document.body.innerText);
  console.log('文档内容:\n', content.substring(0, 5000));
  
  await browser.close();
})();
