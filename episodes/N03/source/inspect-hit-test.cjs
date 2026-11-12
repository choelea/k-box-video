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
  await page.click('.el-menu-item:has-text("检索服务")');
  await page.waitForTimeout(3000);
  
  // 点击"命中测试"标签
  console.log('=== 点击"命中测试" ===');
  await page.click('text=命中测试');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-hit-test.png' });
  
  const hitTestContent = await page.evaluate(() => document.body.innerText);
  console.log('命中测试页面:\n', hitTestContent.substring(0, 4000));
  
  // 选择星途售后的检索服务
  console.log('\n=== 选择星途售后服务 ===');
  
  // 尝试找到下拉选择器
  const selects = await page.$$eval('.el-select, select, [class*="select"]', els =>
    els.slice(0, 10).map(e => ({
      class: e.className,
      text: e.textContent?.trim().substring(0, 100)
    }))
  );
  console.log('选择器:', JSON.stringify(selects, null, 2));
  
  // 尝试选择"星途售后-星小秘"
  try {
    await page.click('.el-select');
    await page.waitForTimeout(1000);
    await page.click('.el-select-dropdown__item:has-text("星途售后"), .el-select-dropdown__item:has-text("qwmytgjn")');
    await page.waitForTimeout(2000);
  } catch (e) {
    console.log('Select error:', e.message);
  }
  
  // 输入测试问题
  console.log('\n=== 输入测试问题 ===');
  const question = '车辆维修后同一故障复发，应该如何处理？';
  
  try {
    const input = await page.locator('textarea, input[type="text"]').first();
    await input.fill(question);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'frames/v3-hit-test-question.png' });
    
    // 点击搜索/测试按钮
    await page.click('button:has-text("搜索"), button:has-text("测试"), button:has-text("检索")');
    await page.waitForTimeout(5000);
    
    await page.screenshot({ path: 'frames/v3-hit-test-result.png' });
    
    const resultContent = await page.evaluate(() => document.body.innerText);
    console.log('测试结果:\n', resultContent.substring(0, 6000));
    
  } catch (e) {
    console.log('Input error:', e.message);
  }
  
  await browser.close();
})();
