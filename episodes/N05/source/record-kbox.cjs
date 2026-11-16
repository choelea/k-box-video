/**
 * N05 自动录屏脚本：登录K-BOX系统，录制图谱详情和智能体问答
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'http://47.94.214.243:32121';
const USERNAME = 'zhangqyu';
const PASSWORD = '5MZXF$$uun';

const TEMP_DIR = path.join(__dirname, '..', 'temp');
const REC_DIR = path.join(__dirname, '..', 'assets', 'recordings');

[TEMP_DIR, REC_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function login(page) {
  console.log('登录中...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle', timeout: 60000 });
  await sleep(1500);

  const inputs = await page.$$('input');
  for (const input of inputs) {
    const type = await input.getAttribute('type');
    if (type === 'text') await input.fill(USERNAME);
    else if (type === 'password') await input.fill(PASSWORD);
  }

  await page.click('button:has-text("下一步")');
  await sleep(3000);

  const kbox = await page.$('text=知识平台研发团队KBOX');
  if (kbox) {
    await kbox.click();
    await sleep(3000);
  }
  console.log('登录成功！');
}

async function recordGraphDemo(page) {
  console.log('\n=== 录制1：图谱详情展示 ===');

  // 进入企业知识库 → 图谱库 → 新能源汽车归档
  await page.click('text=企业知识库');
  await sleep(1500);
  await page.click('text=图谱库');
  await sleep(2500);
  await page.click('text=新能源汽车归档');
  await sleep(3000);
  console.log('已进入新能源汽车归档');

  // 切换到图谱tab
  const graphTab = await page.$('button:has-text("图谱"), .graph-subnav-item:has-text("图谱")');
  if (graphTab) {
    await graphTab.click();
    console.log('已切换到图谱tab');
    await sleep(10000); // 等待图谱完全加载
  }

  await page.screenshot({ path: path.join(TEMP_DIR, 'graph-loaded.png') });
  console.log('图谱已加载');

  // 使用mouse直接在canvas中点击节点
  const canvas = await page.$('canvas');
  if (canvas) {
    const box = await canvas.boundingBox();
    console.log(`Canvas: ${Math.round(box.width)}x${Math.round(box.height)} at (${Math.round(box.x)}, ${Math.round(box.y)})`);

    // 尝试在canvas不同位置点击，查找BMS2026-B08
    const positions = [
      { x: 0.25, y: 0.35, label: '左上' },
      { x: 0.5, y: 0.35, label: '中上' },
      { x: 0.75, y: 0.35, label: '右上' },
      { x: 0.3, y: 0.5, label: '左中' },
      { x: 0.5, y: 0.5, label: '中心' },
      { x: 0.7, y: 0.5, label: '右中' },
      { x: 0.35, y: 0.65, label: '左下' },
      { x: 0.5, y: 0.65, label: '中下' },
      { x: 0.65, y: 0.65, label: '右下' },
      { x: 0.4, y: 0.4, label: '偏左上' },
      { x: 0.6, y: 0.4, label: '偏右上' },
      { x: 0.4, y: 0.6, label: '偏左下' },
      { x: 0.6, y: 0.6, label: '偏右下' }
    ];

    let found = false;
    for (let i = 0; i < positions.length; i++) {
      const pos = positions[i];
      const cx = box.x + box.width * pos.x;
      const cy = box.y + box.height * pos.y;

      await page.mouse.click(cx, cy);
      await sleep(2000);

      // 检查是否出现详情信息
      const visibleText = await page.evaluate(() => {
        const els = document.querySelectorAll('.node-detail, .detail-panel, [class*="detail"], [class*="drawer"], [class*="sidebar"]');
        return Array.from(els).map(e => e.textContent?.trim().substring(0, 200)).filter(t => t);
      });

      if (visibleText.length > 0) {
        console.log(`[${pos.label}] 点击后出现面板: ${visibleText[0]?.substring(0, 100)}`);
        await page.screenshot({ path: path.join(TEMP_DIR, `node-click-${i}-${pos.label}.png`) });

        if (visibleText.some(t => t.includes('BMS'))) {
          console.log('>>> 找到BMS2026-B08节点！');
          found = true;
          break;
        }
      } else {
        // 检查canvas外是否有文本出现
        const bodyText = await page.evaluate(() => {
          return document.body.innerText.substring(0, 500);
        });
        if (bodyText.includes('BMS2026')) {
          console.log(`[${pos.label}] 页面中出现BMS文本！`);
          await page.screenshot({ path: path.join(TEMP_DIR, `node-click-${i}-${pos.label}.png`) });
          found = true;
          break;
        }
      }
    }

    if (!found) {
      console.log('未在canvas中找到BMS节点，尝试更多位置...');
    }

    // 获取点击后的详情面板内容
    const allPanels = await page.evaluate(() => {
      const results = [];
      // 查找所有可能的详情面板
      const selectors = '.node-detail, .detail-panel, .detail-drawer, [class*="detail"], [class*="drawer"], [class*="panel"], [class*="info-panel"], [class*="properties"]';
      document.querySelectorAll(selectors).forEach(el => {
        const text = el.textContent?.trim();
        if (text && text.length > 10 && text.length < 2000) {
          results.push({ class: el.className?.substring(0, 50), text: text.substring(0, 500) });
        }
      });
      return results;
    });
    console.log('\n详情面板:', JSON.stringify(allPanels, null, 2));

    // 获取所有tooltip/popover
    const tooltips = await page.evaluate(() => {
      const results = [];
      document.querySelectorAll('.el-tooltip__popper, .el-popover, [class*="tooltip"], [class*="popover"], [role="tooltip"]').forEach(el => {
        const text = el.textContent?.trim();
        if (text && text.length > 2) {
          results.push(text.substring(0, 300));
        }
      });
      return results;
    });
    if (tooltips.length > 0) {
      console.log('Tooltips:', JSON.stringify(tooltips, null, 2));
    }

    // 获取图谱中所有可见的节点标签
    const nodeLabels = await page.evaluate(() => {
      const labels = [];
      // 查找SVG text或div标签
      document.querySelectorAll('.node-label, [class*="node"] text, .g6-node-label, text[class*="label"]').forEach(el => {
        const text = el.textContent?.trim();
        if (text && text.length > 1) {
          labels.push(text);
        }
      });
      return labels;
    });
    if (nodeLabels.length > 0) {
      console.log('节点标签:', JSON.stringify(nodeLabels, null, 2));
    }

    // 最终截图
    await page.screenshot({ path: path.join(TEMP_DIR, 'graph-final.png') });
  }

  console.log('图谱录制完成');
}

async function recordAgentDemo(page) {
  console.log('\n=== 录制2：智能体问答 ===');

  await page.click('text=智能体中心');
  await sleep(3000);

  // 滚动查找星途故障推理
  await page.evaluate(() => {
    const container = document.querySelector('.page-content, .chatapp-grid, main');
    if (container) container.scrollTop = container.scrollHeight;
  });
  await sleep(1500);

  // 精确查找星途故障推理卡片的h3标题
  const agentCards = await page.$$('h3.card-name');
  let agentCard = null;
  for (const card of agentCards) {
    const text = await card.textContent();
    console.log(`  智能体: ${text?.trim()}`);
    if (text && text.trim() === '星途故障推理') {
      agentCard = card;
      break;
    }
  }

  if (agentCard) {
    // 点击卡片进入智能体对话页面
    await agentCard.click();
    console.log('已进入星途故障推理');
    await sleep(5000);
    await page.waitForLoadState('networkidle');

    await page.screenshot({ path: path.join(TEMP_DIR, 'agent-page.png') });
    console.log('当前URL:', page.url());

    // 打印对话页面所有元素
    const dialogElements = await page.$$eval('*', els =>
      els.filter(e => e.children.length === 0 && e.textContent?.trim().length > 2)
         .slice(0, 50)
         .map(e => ({ text: e.textContent?.trim().substring(0, 100), tag: e.tagName, class: e.className?.substring(0, 40) }))
    );
    console.log('对话页面元素:', JSON.stringify(dialogElements, null, 2));

    // 查找预置问题 - 尝试多种class名
    const presetSelectors = [
      '.preset-question', '.suggestion-item', '.quick-question', '.example-question',
      '.prompt-item', '.starter-question', '.quick-start', '.recommended-question',
      '[class*="preset"]', '[class*="suggestion"]', '[class*="quick"]', '[class*="example"]',
      '[class*="starter"]', '[class*="recommend"]'
    ];

    let presets = [];
    for (const sel of presetSelectors) {
      const found = await page.$$(sel);
      if (found.length > 0) {
        presets = found;
        console.log(`选择器 ${sel} 找到 ${found.length} 个元素`);
        break;
      }
    }

    if (presets.length === 0) {
      // 尝试查找对话区域内的可点击文本
      console.log('未找到标准预置问题元素，查找可点击的短文本...');
      const shortTexts = await page.$$eval('div, span, p, button, a', els =>
        els.filter(e => {
          const text = e.textContent?.trim();
          const cls = e.className || '';
          return text && text.length > 5 && text.length < 150 &&
                 (text.includes('?') || text.includes('？') || cls.includes('question') || cls.includes('prompt'));
        }).slice(0, 15).map(e => ({
          text: e.textContent?.trim().substring(0, 100),
          tag: e.tagName,
          class: e.className?.substring(0, 50),
          clickable: e.tagName === 'BUTTON' || e.tagName === 'A' || e.onclick !== null
        }))
      );
      console.log('可能的预置问题:', JSON.stringify(shortTexts, null, 2));
    }

    if (presets.length > 0) {
      for (let i = 0; i < presets.length; i++) {
        const text = await presets[i].textContent();
        console.log(`  预置${i}: ${text?.trim().substring(0, 80)}`);
      }

      // 点击第一个预置问题
      const qText = await presets[0].textContent();
      console.log(`\n点击第一个预置问题: ${qText?.trim().substring(0, 60)}`);
      await presets[0].click();
      console.log('等待回答加载...');
      await sleep(20000); // 等待更长时间确保回答完全加载

      await page.screenshot({ path: path.join(TEMP_DIR, 'agent-answer.png') });

      // 获取完整回答内容
      const answers = await page.$$eval('[class*="message"], [class*="answer"], [class*="response"], [class*="bubble"], [class*="content"]', els =>
        els.map(e => e.textContent?.trim()).filter(t => t && t.length > 20).map(t => t.substring(0, 800))
      );
      console.log('\n回答内容:', JSON.stringify(answers, null, 2));
    }
  } else {
    console.log('未找到星途故障推理智能体');

    // 列出所有智能体
    const allAgents = await page.$$eval('h3.card-name', els =>
      els.map(e => e.textContent?.trim())
    );
    console.log('所有智能体:', allAgents);
  }

  console.log('智能体录制完成');
}

async function main() {
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: REC_DIR,
      size: { width: 1920, height: 1080 }
    }
  });

  const page = await context.newPage();

  await login(page);
  await recordGraphDemo(page);
  await recordAgentDemo(page);

  console.log('\n=== 全部录制完成 ===');

  await sleep(2000);
  await context.close();
  await browser.close();

  // 列出录屏文件
  const files = fs.readdirSync(REC_DIR);
  console.log('\n录屏文件列表:');
  files.forEach(f => {
    const stat = fs.statSync(path.join(REC_DIR, f));
    console.log(`  ${f} (${(stat.size / 1024 / 1024).toFixed(1)} MB)`);
  });
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
