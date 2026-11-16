/**
 * N05 截图脚本：登录K-BOX系统，截取知识图谱相关页面
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'http://47.94.214.243:32121';
const LOGIN_URL = `${BASE_URL}/login`;
const USERNAME = 'zhangqyu';
const PASSWORD = '5MZXF$$uun';

const FRAMES_DIR = path.join(__dirname, '..', 'frames');
const TEMP_DIR = path.join(__dirname, '..', 'temp');

// 确保目录存在
[FRAMES_DIR, TEMP_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  console.log('正在登录K-BOX系统...');
  await page.goto(LOGIN_URL, { waitUntil: 'networkidle', timeout: 60000 });

  // 等待登录表单加载
  await page.waitForSelector('input', { timeout: 15000 });
  await sleep(1500);

  // 找到所有input并填写
  const inputs = await page.$$('input');
  console.log(`找到 ${inputs.length} 个输入框`);

  for (const input of inputs) {
    const type = await input.getAttribute('type');
    const placeholder = await input.getAttribute('placeholder');
    console.log(`  输入框: type=${type}, placeholder=${placeholder}`);

    if (type === 'text' || (placeholder && (placeholder.includes('账号') || placeholder.includes('用户名')))) {
      await input.click();
      await input.fill(USERNAME);
      console.log('  已填写用户名');
    } else if (type === 'password') {
      await input.click();
      await input.fill(PASSWORD);
      console.log('  已填写密码');
    }
  }

  await sleep(500);

  // 点击"下一步"按钮
  const nextBtn = await page.$('button:has-text("下一步"), button[type="submit"]');
  if (nextBtn) {
    console.log('点击下一步按钮...');
    await nextBtn.click();
  }

  // 等待登录成功并跳转
  console.log('等待登录跳转...');
  try {
    await page.waitForURL('**/chatapps**', { timeout: 15000 });
    console.log('已跳转到chatapps');
  } catch (e) {
    console.log('等待跳转超时，尝试手动导航...');
    // 可能需要先登录再访问
    const currentUrl = page.url();
    console.log('当前URL:', currentUrl);

    // 如果有redirect参数，提取并跳转
    if (currentUrl.includes('redirect=')) {
      const redirectUrl = currentUrl.match(/redirect=([^&]+)/)?.[1];
      if (redirectUrl) {
        console.log('尝试跳转到:', redirectUrl);
        await page.goto(BASE_URL + redirectUrl, { waitUntil: 'networkidle', timeout: 30000 });
      }
    }
  }

  await sleep(2000);

  // 检查是否出现租户选择页面
  const tenantPage = await page.$('text=选择租户');
  if (tenantPage) {
    console.log('检测到租户选择页面...');

    // 尝试选择"知识平台研发团队KBOX"租户（优先）
    let tenant = await page.$('text=知识平台研发团队KBOX');
    if (!tenant) tenant = await page.$(':text("KBOX")');
    if (!tenant) tenant = await page.$(':text("测试租户")');
    if (!tenant) {
      // 选择第一个租户卡片
      const tenantCards = await page.$$('.tenant-card, [class*="tenant"], [class*="space"]');
      if (tenantCards.length > 0) {
        tenant = tenantCards[0];
      }
    }

    if (tenant) {
      await tenant.click();
      console.log('已选择租户');
      await sleep(3000);
      await page.waitForLoadState('networkidle');
    }
  }

  console.log('登录完成！当前URL:', page.url());

  // 截图1：首页/导航
  await page.screenshot({ path: path.join(TEMP_DIR, 'home.png'), fullPage: false });
  console.log('截图: home.png');

  // 导航到企业知识库 → 图谱库
  console.log('\n正在导航到图谱库...');

  // 打印页面上所有可见的文本链接用于调试
  const allLinks = await page.$$eval('a, button, [role="menuitem"], .menu-item, span, div',
    els => els.slice(0, 50).map(e => ({ text: e.textContent?.trim().substring(0, 30), tag: e.tagName }))
  );
  console.log('页面元素(前50个):', JSON.stringify(allLinks.filter(l => l.text), null, 2));

  // 尝试点击企业知识库菜单
  let enterpriseKB = await page.$(':text("企业知识库")');
  if (!enterpriseKB) enterpriseKB = await page.$('text=企业知识库');
  if (!enterpriseKB) enterpriseKB = await page.$('[title="企业知识库"]');
  if (enterpriseKB) {
    await enterpriseKB.click();
    await sleep(2000);
    console.log('已点击企业知识库');
  } else {
    console.log('未找到企业知识库入口');
  }

  // 尝试点击图谱库
  let graphLib = await page.$(':text("图谱库")');
  if (!graphLib) graphLib = await page.$('text=图谱库');
  if (!graphLib) graphLib = await page.$('a:has-text("图谱")');
  if (!graphLib) graphLib = await page.$('[title*="图谱"]');
  if (graphLib) {
    await graphLib.click();
    await sleep(2500);
    console.log('已点击图谱库');
  } else {
    console.log('未找到图谱库入口，尝试直接导航...');
    // 尝试通过URL直接访问
    await page.goto(BASE_URL + '/graph', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
    await sleep(2000);
  }

  // 截图2：图谱库列表
  await page.screenshot({ path: path.join(TEMP_DIR, 'graph-list.png'), fullPage: false });
  console.log('截图: graph-list.png');
  console.log('当前URL:', page.url());

  // 查找并点击"新能源汽车归档"
  console.log('\n正在查找新能源汽车归档...');

  // 先看看左侧目录树
  const sidebarItems = await page.$$eval('.sidebar-item, .tree-node, .folder-item, [class*="tree"], [class*="folder"], [class*="dir"]', els =>
    els.map(e => ({ text: e.textContent?.trim().substring(0, 60), class: e.className?.substring(0, 50) }))
  );
  console.log('侧边栏/目录项:', JSON.stringify(sidebarItems.slice(0, 20), null, 2));

  // 尝试通过面包屑导航回到上级目录
  const breadcrumb = await page.$('.el-breadcrumb, [class*="breadcrumb"]');
  if (breadcrumb) {
    const bcText = await breadcrumb.textContent();
    console.log('面包屑:', bcText);

    // 点击"企业知识库"回到根目录
    const kbLink = await page.$('.el-breadcrumb a:has-text("企业知识库"), .breadcrumb a:first-child');
    if (kbLink) {
      await kbLink.click();
      await sleep(2000);
      console.log('已回到企业知识库根目录');
    }
  }

  // 再次查找新能源汽车归档
  let evGraph = await page.$(':text("新能源汽车归档")');
  if (!evGraph) evGraph = await page.$('text=新能源汽车归档');
  if (!evGraph) evGraph = await page.$('text=新能源');
  if (!evGraph) evGraph = await page.$('[title*="新能源"]');
  if (!evGraph) evGraph = await page.$('span:has-text("新能源")');

  if (evGraph) {
    console.log('找到新能源汽车归档！');
    await evGraph.click();
    await sleep(3000);
    await page.waitForLoadState('networkidle');
  } else {
    console.log('未直接找到，尝试浏览所有目录项...');
    // 列出所有可点击的目录项
    const allDirs = await page.$$('.folder-item, .tree-node-content, [class*="folder"], [class*="dir"]');
    for (const dir of allDirs) {
      const text = await dir.textContent();
      console.log('  目录项:', text?.trim().substring(0, 40));
      if (text && (text.includes('新能源') || text.includes('归档'))) {
        await dir.click();
        await sleep(2000);
        console.log('  已点击进入:', text.trim().substring(0, 40));
        break;
      }
    }
  }

  // 截图3：图谱库详情页
  await page.screenshot({ path: path.join(TEMP_DIR, 'graph-detail.png'), fullPage: false });
  console.log('截图: graph-detail.png');
  console.log('当前URL:', page.url());

  // 尝试查看图谱可视化
  await sleep(2000);
  await page.screenshot({ path: path.join(TEMP_DIR, 'graph-visual.png'), fullPage: false });
  console.log('截图: graph-visual.png');

  // 导航到智能体中心
  console.log('\n正在导航到智能体中心...');

  // 尝试多种方式找到智能体中心
  let agentCenter = await page.$(':text("智能体中心")');
  if (!agentCenter) agentCenter = await page.$('text=智能体中心');
  if (!agentCenter) agentCenter = await page.$('a:has-text("智能体")');
  if (!agentCenter) agentCenter = await page.$('[title*="智能体"]');

  if (agentCenter) {
    await agentCenter.click();
    await sleep(2500);
    console.log('已点击智能体中心');
  } else {
    console.log('未找到智能体中心入口，尝试URL导航...');
    await page.goto(BASE_URL + '/agent', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
    await sleep(2000);
  }

  // 截图4：智能体中心列表
  await page.screenshot({ path: path.join(TEMP_DIR, 'agent-list.png'), fullPage: false });
  console.log('截图: agent-list.png');
  console.log('当前URL:', page.url());

  // 打印页面元素用于调试
  const agentPageContent = await page.$$eval('*', els =>
    els.filter(e => e.textContent?.includes('星途') || e.textContent?.includes('故障'))
       .slice(0, 20)
       .map(e => ({ text: e.textContent?.trim().substring(0, 50), tag: e.tagName, class: e.className?.substring(0, 30) }))
  );
  console.log('包含关键词的元素:', JSON.stringify(agentPageContent, null, 2));

  // 查找并点击"星途故障推理"
  console.log('\n正在查找星途故障推理...');

  // 先滚动页面查看所有智能体
  await page.evaluate(() => {
    const container = document.querySelector('.page-content, .chatapp-grid, main');
    if (container) container.scrollTop = container.scrollHeight;
  });
  await sleep(1500);

  // 打印所有智能体卡片名称
  const allAgents = await page.$$eval('.app-card, .card-name, [class*="card"] h3, [class*="card"] [class*="name"]', els =>
    els.map(e => e.textContent?.trim().substring(0, 60))
  );
  console.log('所有智能体:', JSON.stringify(allAgents, null, 2));

  // 截取滚动后的截图
  await page.screenshot({ path: path.join(TEMP_DIR, 'agent-list-full.png'), fullPage: false });
  console.log('截图: agent-list-full.png');

  let starAgent = await page.$(':text("星途故障推理")');
  if (!starAgent) starAgent = await page.$('text=星途故障推理');
  if (!starAgent) starAgent = await page.$('text=故障推理');
  if (!starAgent) starAgent = await page.$('[title*="故障"]');

  if (starAgent) {
    await starAgent.click();
    await sleep(3000);
    await page.waitForLoadState('networkidle');

    // 截图5：星途故障推理详情
    await page.screenshot({ path: path.join(TEMP_DIR, 'agent-detail.png'), fullPage: false });
    console.log('截图: agent-detail.png');

    // 尝试进入对话界面
    let chatBtn = await page.$(':text("对话")');
    if (!chatBtn) chatBtn = await page.$('text=问答');
    if (!chatBtn) chatBtn = await page.$('text=开始对话');
    if (!chatBtn) chatBtn = await page.$('button:has-text("对话")');

    if (chatBtn) {
      await chatBtn.click();
      await sleep(2000);
      await page.screenshot({ path: path.join(TEMP_DIR, 'agent-chat.png'), fullPage: false });
      console.log('截图: agent-chat.png');
    }
  } else {
    console.log('未找到"星途故障推理"，尝试搜索...');
    const searchInput = await page.$('input[type="search"], input[placeholder*="搜索"], input.search-input');
    if (searchInput) {
      const tagName = await searchInput.evaluate(el => el.tagName);
      if (tagName === 'INPUT' || tagName === 'TEXTAREA') {
        await searchInput.fill('星途');
        await sleep(2000);
        await page.screenshot({ path: path.join(TEMP_DIR, 'agent-search.png'), fullPage: false });
        console.log('已尝试搜索');
      }
    }
  }

  console.log('\n截图完成！文件保存在 temp/ 目录');

  await sleep(2000);
  await browser.close();
}

main().catch(err => {
  console.error('脚本执行出错:', err);
  process.exit(1);
});
