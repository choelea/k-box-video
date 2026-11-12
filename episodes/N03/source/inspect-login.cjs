const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('http://47.94.214.243:32121/login', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);
  
  // 填写用户名密码
  await page.fill('input[placeholder*="邮箱/手机号/用户代码"]', 'zhangqyu');
  await page.fill('input[placeholder*="密码"]', '5MZXF$$uun');
  await page.click('button:has-text("下一步")');
  await page.waitForTimeout(5000);
  
  console.log('After login URL:', page.url());
  
  // 检查是否有租户选择
  const content = await page.content();
  if (content.includes('知识平台研发团队')) {
    console.log('Tenant selection found');
    await page.click('text=知识平台研发团队');
    await page.waitForTimeout(3000);
  }
  
  console.log('Final URL:', page.url());
  
  // 等待主界面加载
  await page.waitForTimeout(3000);
  
  // 截取登录后页面
  const framesDir = path.join(__dirname, '..', 'frames');
  await page.screenshot({ path: path.join(framesDir, 'after-login.png'), fullPage: true });
  
  // 检查菜单结构
  const menuItems = await page.$$eval('[class*="menu"], [class*="nav"], aside a, .sidebar a', els => 
    els.slice(0, 20).map(e => ({ text: e.textContent?.trim(), href: e.href, class: e.className }))
  );
  console.log('Menu items:', JSON.stringify(menuItems, null, 2));
  
  await browser.close();
})().catch(e => console.error('Error:', e.message));
