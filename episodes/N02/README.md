# N02 · 已有文档系统和大模型，为什么还需要 K-BOX？

当前为 **企业场景优化版 v2**，约 4 分 32 秒。新能源汽车售后质量处置：异常反馈 → 深度检索三份制度 → 单车与批次建议 → 原文核对。业务输入为已标注的假设，本集不展开权限。

- [试看页](试看.html)、[成片](N02-企业场景版.mp4)、[字幕](N02-企业场景版.srt)、[配音](N02-企业场景版-配音.mp3)、[讲解稿](讲解稿.md)。
- [讲解源](source/plan.json)、[语音辅助文本](source/speech-overrides.json)、[字幕语义分句](source/subtitle-phrases.json)。
- [可编辑图解](source/scenes.json)、[视觉 HTML](source/slides.html)、[品牌基础样式](../../shared/brand/v0.1/visual/base.css)、[分镜时点](source/shots.json)。
- 原始录屏：assets/recordings/；配音与截图：audio/、frames/；[素材清单](assets.json)。
- [制作记录](source/production-notes.md)、[修订记录](review/revisions/revision-v2.json)、[待审阅项](episode.json)。

已应用确认的 C 配音方案与深蓝金色模板，片头品牌问句复用已确认同句音频；另外两个新语境待核听。原真实问答与引用保持，采用同一批已核验录屏与截图。此次优化未重新访问线上应用。

优化前企业版与电影版通过 [Git 历史记录](../../reports/history/历史版本.json) 恢复，不再保留目录副本。

## 继续修改

从仓库根目录执行：

```bash
python tools/video.py check N02
python tools/video.py render N02
python tools/video.py serve N02 --port 8769
```

修改讲解文字后运行 source/narrate.py 生成配音时间线。该脚本只为 speech-overrides.json 中明确指定的品牌段重新合成，其他段复用保存音频；若修改其他口播，应更新相应语音文件或扩展生成配置，不能仅修改 plan.json。

subtitle-phrases.json 存放长句的人工语义断句。assemble.py 通过字幕文本或段落定位切镜，改动锚点句后需要同步修改锚点；定位不到会明确报错，不沿用旧时点。图解内容维护在 scenes.json；tools/capture-brand.cjs N02 会同步 HTML 中内嵌场景后录图。

render 使用保存素材，不自动重做配音或截图。先完成上述内容更新再导出，并刷新素材清单与核验记录。

2026-11-03 品牌层级纠正待办：当前成片中“问学的售后知识库”“问学带来的”误以品牌代指产品；下一版须使用“问学知识平台”或“K-BOX”，并同步配音、字幕与镜头。目前尚未重制这两句，见 episode.json。

目录说明：source/ 是制作脚本和配置，frames/ 是制作及证据画面，review/ 保存当前验收截图与核验，review/revisions/ 保存修订日志。播放与截图检查不代表核听通过。配音只读检查：`python episodes/N02/source/narrate.py --check-only`。
