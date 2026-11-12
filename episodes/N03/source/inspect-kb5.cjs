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
  
  // 点击"中国电影 TOP500"知识库
  console.log('=== 点击"中国电影 TOP500"知识库 ===');
  await page.click('text=中国电影 TOP500');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-document-movies.png' });
  
  const moviesText = await page.evaluate(() => {
    const main = document.querySelector('.main-content, .content-area, main');
    return main ? main.innerText : document.body.innerText;
  });
  console.log('页面文本:\n', moviesText.substring(0, 2000));
  
  // 返回并查看 Wiki 库
  console.log('\n=== 查看 Wiki 库 ===');
  await page.click('.el-menu-item:has-text("企业知识库")');
  await page.waitForTimeout(2000);
  await page.click('.kb-card-title-main:has-text("Wiki库")');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-wiki-detail.png' });
  
  const wikiText = await page.evaluate(() => {
    const main = document.querySelector('.main-content, .content-area, main');
    return main ? main.innerText : document.body.innerText;
  });
  console.log('Wiki库文本:\n', wikiText.substring(0, 2000));
  
  // 查看图谱库
  console.log('\n=== 查看图谱库 ===');
  await page.click('.el-menu-item:has-text("企业知识库")');
  await page.waitForTimeout(2000);
  await page.click('.kb-card-title-main:has-text("图谱库")');
  await page.waitForTimeout(3000);
  
  console.log('URL:', page.url());
  await page.screenshot({ path: 'frames/v3-graph-detail.png' });
  
  const graphText = await page.evaluate(() => {
    const main = document.querySelector('.main-content, .content-area, main');
    return main ? main.innerText : document.body.innerText;
  });
  console.log('图谱库文本:\n', graphText.substring(0, 1500));
  
  await browser.close();
})();
