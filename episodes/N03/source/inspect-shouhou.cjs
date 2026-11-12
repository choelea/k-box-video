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
  
  // 点击"星途新能源"
  await page.click('.kb-card-title-main:has-text("星途新能源")');
  await page.waitForTimeout(3000);
  
  // 点击"售后知识库"
  console.log('=== 点击"售后知识库" ===');
  await page.click('.kb-card-title-main:has-text("售后知识库")');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-shouhou-files.png' });
  
  const shouhouText = await page.evaluate(() => document.body.innerText);
  console.log('售后知识库文本:\n', shouhouText.substring(0, 4000));
  
  await browser.close();
})();
