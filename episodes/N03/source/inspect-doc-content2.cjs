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
  
  // 尝试点击操作按钮查看详情
  console.log('=== 尝试查看文档详情 ===');
  
  // 获取操作按钮
  const ops = await page.$$eval('button, .el-button, [class*="action"], [class*="more"]', els =>
    els.slice(0, 30).map(e => ({
      text: e.textContent?.trim(),
      class: e.className,
      title: e.title
    }))
  );
  console.log('操作按钮:', JSON.stringify(ops.filter(o => o.text || o.title), null, 2));
  
  // 尝试点击"已就绪"标签或文档行
  await page.locator('tr:has-text("星途新能源售后质量处置指引")').click();
  await page.waitForTimeout(3000);
  
  console.log('URL after click:', page.url());
  await page.screenshot({ path: 'frames/v3-doc-content-1.png' });
  
  // 获取页面主要内容
  const mainContent = await page.evaluate(() => {
    // 尝试获取弹窗、抽屉或新页面的内容
    const dialog = document.querySelector('.el-dialog, .el-drawer, .doc-preview, .markdown-body');
    if (dialog) return dialog.innerText;
    return document.body.innerText;
  });
  console.log('主要内容:\n', mainContent.substring(0, 5000));
  
  await browser.close();
})();
