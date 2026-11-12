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
  
  // 点击"星途新能源"知识库
  console.log('=== 点击"星途新能源"知识库 ===');
  await page.click('.kb-card-title-main:has-text("星途新能源")');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-xingtu-detail.png' });
  
  const xingtuText = await page.evaluate(() => document.body.innerText);
  console.log('星途新能源文本:\n', xingtuText.substring(0, 3000));
  
  // 尝试进入子目录或查看文件
  console.log('\n=== 尝试查看子内容 ===');
  
  // 获取所有可点击元素
  const clickables = await page.$$eval('.kb-card-title-main, .file-name, .doc-name, a', els =>
    els.slice(0, 20).map(e => ({
      text: e.textContent?.trim(),
      tag: e.tagName,
      href: e.href || ''
    }))
  );
  console.log('可点击元素:', JSON.stringify(clickables, null, 2));
  
  await browser.close();
})();
