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
  await page.click('.kb-card-title-main:has-text("文档库")');
  await page.waitForTimeout(3000);
  
  console.log('=== 文档库详情页 ===');
  console.log('URL:', page.url());
  
  // 等待页面加载并截图
  await page.screenshot({ path: 'frames/v3-document-files.png', fullPage: true });
  
  // 获取文件列表 - 尝试更多选择器
  const allText = await page.evaluate(() => {
    const main = document.querySelector('.main-content, .content-area, main');
    return main ? main.innerText : document.body.innerText;
  });
  console.log('页面文本:\n', allText.substring(0, 2000));
  
  // 导航到智能体中心进行问答测试
  console.log('\n=== 导航到智能体中心 ===');
  await page.click('.el-menu-item:has-text("智能体中心")');
  await page.waitForTimeout(3000);
  
  await page.screenshot({ path: 'frames/v3-agent-chat.png' });
  
  // 查看是否有可用的智能体
  const agents = await page.$$eval('.agent-card, .chat-item, [class*="agent"]', els =>
    els.slice(0, 10).map(e => ({
      text: e.textContent?.trim().substring(0, 100),
      class: e.className
    }))
  );
  console.log('智能体列表:', JSON.stringify(agents, null, 2));
  
  await browser.close();
})();
