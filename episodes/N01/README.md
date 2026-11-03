# N01 · 问学知识平台基础介绍

当前 v3 约 3 分 52 秒，覆盖产品定位、产品能力、知识消费、应用场景、企业级保障和文档中心。

- [试看页](试看.html)、[成片](问学知识平台-基础介绍.mp4)、[讲解稿](讲解稿.md)。
- [字幕](问学知识平台-基础介绍.srt)、[配音](问学知识平台-中文配音.mp3)。
- 配音文本源：[source/plan.json](source/plan.json)，发音辅助文本：[source/speech-overrides.json](source/speech-overrides.json)。
- 时间线：[source/timeline.json](source/timeline.json)，镜头：[source/shots.json](source/shots.json)。
- 六段新录屏及旧原片均在 assets/recordings/；来源文字快照在 source/；截图在 frames/。
- [状态及待审项](episode.json)、[制作说明](制作说明.md)。

2026-11-03 依据官网更新重制：菜单、画面、配音、字幕和章节统一为“文档中心”；同步“API 参考”栏目名称。六个公开页面重新采集，品牌读音采用已确认 C 方案，视觉采用深蓝金色 v0.1。三处品牌新语境及整片仍待用户核听。

v3 已将定位句纠正为“问学知识平台位于企业知识和上层智能体之间”，区分上位品牌问学与产品 K-BOX。v2 保存在 [archive/N01-intro-v2](../../archive/N01-intro-v2/README.md)。

首次重制前完整项目保存在 [archive/N01-intro-v1](../../archive/N01-intro-v1/README.md)。不需要登录，不执行线上问答或修改后台数据。

在仓库根目录用 `python tools/video.py check N01` 核验；`python tools/video.py render N01` 使用现有素材离线导出。配音变更时先同步 plan.json 与 speech-overrides.json，再运行 source/narrate.py；它仅更新覆盖表中请求有变化的片段并重建时间线。其他语句修改须加入覆盖表，不能只改阅读稿。随后应重录受影响画面并重新导出。

重新采集页面：设置 Playwright 依赖后依次运行 source/inspect.cjs、source/record.cjs、source/calibrate-recordings.py、source/capture-docs.cjs；品牌页面截图用 source/capture-brand.cjs。record.cjs 按时间线实录六个章节，可能受网站布局变化影响，需核对全部高亮目标。
