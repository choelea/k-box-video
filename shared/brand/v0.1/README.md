# 品牌读音与视觉风格 · v0.1

2026-11-02 用户已确认 **C 读音与深蓝金色视觉风格**，本版作为后续视频统一制作基线。选定入口为 ../active.json。N02 v2 已应用本基线；N01 的旧配音仍待单独修正。

- [试看与试听](试看.html)：四套候选、30 秒样片与四种公共画面。
- [样片 MP4](品牌风格样片.mp4)、[样片字幕](品牌风格样片.srt)、[视觉总览](visual/风格总览.jpg)。
- [语音测试源](source/voice-plan.json)：正式写法与合成输入分别保存。
- [视觉参数](visual/tokens.json)、[可编辑模板](visual/template.html)。
- [品牌发音规范](../../../standards/品牌与发音.md)、[视觉风格规范](../../../standards/视觉风格.md)。

## 读音候选

| 候选 | 音色 | 合成输入中的品牌写法 | 用途 |
| --- | --- | --- | --- |
| A | 晓晓女声 | 问学知识平台 | 原始读法对照 |
| B | 晓晓女声 | 问学，知识平台 | 测试品牌后语气边界 |
| C | 晓晓女声 | “问学”知识平台 | 已确认的后续配音方案 |
| D | 云希男声 | 问学，知识平台 | 比较音色与品牌后分句效果 |

均使用 edge-tts、语速 +12%，每套测试独立名称、欢迎语和 N02 片头问题三个语境。保留每句音频、请求参数和词边界记录。引号或逗号是当前引擎的试验方法，不是受支持的自定义发音词典。

三个语境的元数据中，A 将“问”“学”分开，B/C/D 将“问学”标为一词。用户已核听并确认 C 读音没有问题，采用 C 作为后续配音方案。词边界本身仍不能代替整片核听；新句子和换引擎后继续核对。

样片仅用于设计审阅，不属于 2–7 分钟正式教程。实操片段使用已保存 N02 真实引用截图；新讲解不声称重新执行过线上问答。默认无背景音乐。

## 继续修改

从仓库根目录执行，Python 依赖沿用 requirements.txt，录图需要 Playwright 和本机 Chrome：

```bash
python shared/brand/v0.1/source/generate_voice.py
node shared/brand/v0.1/source/capture_visuals.cjs
python shared/brand/v0.1/source/render_sample.py
python tools/serve.py . --port 8770
```

访问 `/shared/brand/v0.1/试看.html`。生成脚本会按请求参数复用已生成的句子；改文本、音色或语速会重新生成对应语音。随后仍会重新拼接候选试听音频；样片需要单独重导。

每个请求的音色、语速和原文保存在 voice/*.request.json。视觉颜色、字号与布局在 tokens.json 和 template.html 中同步修改。选定读音已记录在 shared/pronunciation.json，视觉确认记录在 source/review-status.json 与 visual/tokens.json。
