# 问学知识平台 · 视频系列

本仓库保存 K-BOX 视频的选题、规范、制作源文件和交付物，供持续修改与再制作。每条视频 2–7 分钟。当前已迁入 N01 基础介绍、N02 企业场景版，电影场景试片单独归档。

## 从这里开始

- [分类与选题](planning/K-BOX视频系列-分类与选题规划.md)：四个分类、50 个选题及待补充专题。
- [内容主线](planning/K-BOX视频系列-内容主线规划.md)：全平台内容范围。
- [制作与修改规范](standards/制作与修改.md)、[品牌与发音](standards/品牌与发音.md)、[验收标准](standards/验收标准.md)。
- [品牌读音与视觉风格 v0.1](shared/brand/v0.1/README.md)：四组试听、30 秒样片及公共模板，C 读音与深蓝金色视觉均已确认，作为后续统一标准；[视觉规范](standards/视觉风格.md)。
- [N01 基础介绍](episodes/N01/README.md)：约 3:51。
- [N02 企业场景版](episodes/N02/README.md)：当前 v2，约 4:32，深度检索三份售后制度并回读依据。
- [N02 电影场景历史版](archive/N02-movie/README.md)：保留对照，不作为当前制作模板。

N02 已制作应用 C 配音方案与统一视觉的企业场景优化版 v2；优化前企业版与电影版均保留归档。N01 品牌读音仍待修正，新语境与整片仍需核听审阅。

## 已制作视频与配套文件

| 视频 | 成片 | 字幕 | 配音 | 讲解稿 | 完整项目 |
| --- | --- | --- | --- | --- | --- |
| N01 基础介绍 · 3:51 | [MP4](episodes/N01/问学知识平台-基础介绍.mp4) | [SRT](episodes/N01/问学知识平台-基础介绍.srt) | [MP3](episodes/N01/问学知识平台-中文配音.mp3) | [讲解稿](episodes/N01/讲解稿.md) | [素材与制作源文件](episodes/N01/README.md) |
| N02 企业场景优化版 v2 · 4:32 | [MP4](episodes/N02/N02-企业场景版.mp4) | [SRT](episodes/N02/N02-企业场景版.srt) | [MP3](episodes/N02/N02-企业场景版-配音.mp3) | [讲解稿](episodes/N02/讲解稿.md) | [素材与制作源文件](episodes/N02/README.md) |

两条均保留原始录屏、分段配音、截图、图解、分镜、时间线、字幕及合成脚本。2026-11-02 已对照原制作目录复核交付物与原始录屏，素材清单及哈希检查通过。历史电影版另见 archive/N02-movie/。

## 目录与存储

```text
planning/             内容主线、分类选题、场景方案
standards/            制作、品牌发音、验收规则
shared/               公共素材说明
templates/episode/    新视频选题卡与分镜模板
episodes/N01/         基础介绍的完整项目
episodes/N02/         当前 N02 企业场景版完整项目
archive/              历史试片与早期讨论稿
tools/                统一核验、导出、试看入口
```

每条项目保留 `source/` 制作脚本和配置、`audio/` 分段配音及时间信息、`frames/` 截图和图解、`assets/recordings/` 原始录屏、`assets.json` 素材校验清单，以及 MP4、SRT、MP3、试看页和讲解稿。`build/` 只放可再生中间文件。

文本使用普通 Git，视频、音频和位图使用 Git LFS。成片也纳入 LFS，保证当前交付可以找回。后续若迁到对象存储，需维护下载位置和 SHA-256，不能只删除仓库素材。

```bash
git lfs install --local
git lfs pull
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

需要 Python 3.11 或以上，另需系统安装 FFmpeg（含 ffprobe、libass）。当前导入的排版与核验脚本使用 macOS PingFang 字体；其他系统须先配置有授权的中文字体并重新核对排版。浏览器重新录制另需 `npm install`，现有脚本使用本机 Google Chrome；它不是离线合成的必需依赖。

## 常用操作

以下命令从仓库根目录执行。核验和重新导出使用现有录屏、截图及配音，不会访问线上系统或重新调用模型。

```bash
# 检查素材清单、路径、文件哈希、成片规格和全片解码
.venv/bin/python tools/video.py check N02

# 用现有配音与素材重新合成，核验并刷新素材清单
.venv/bin/python tools/video.py render N02

# 本地试看；打开命令输出的地址（支持视频范围请求和拖动）
.venv/bin/python tools/video.py serve N02 --port 8769
```

N01 使用同样命令。工具也支持历史项目路径 `archive/N02-movie`。重新导出会覆盖本地对应成片；历史版本通过 Git 提交保留。提交前将想保留的版本保存为一次独立提交，再继续改动。

## 修改时改哪里

| 修改内容 | 修改入口 | 后续处理 |
| --- | --- | --- |
| 选题与范围 | planning/ | 同步总数、关联主题和选题卡 |
| 讲解内容 | source/plan.json | 同步讲解稿；重做受影响配音、时间线及字幕 |
| 字幕断句 | source/timeline.json 的 cues、独立 SRT | 保持两者一致；重新导出 |
| 图解 | source/slides.html | 重新截图到 frames/，再导出 |
| 实操画面 | assets/recordings/、frames/ | 核对真实操作，更新分镜与素材引用 |
| N02 镜头时长 | source/assemble.py | 与 timeline.json 的配音时点逐项核对 |
| 制作状态和待修项 | episode.json | 技术检查、内容审阅分别记录 |

目前迁入的是已使用的制作脚本，尚未实现完整的分段增量生成。`narrate.py` 会重新合成全部配音并覆盖时间线和阅读稿；不要将它当作无影响的导出步骤。当前 N02 v2 的镜头切换随讲解片段和语义字幕锚点定位；改动锚点文字需同步更新定位配置。后续统一流水线以分镜模板为目标逐步演进。

重新录制需要重新登录，历史会话文件未迁入。管理端和消费端会话通过 `KBOX_MANAGEMENT_STATE`、`KBOX_GUEST_STATE` 环境变量提供；历史电影版使用 `KBOX_BROWSER_STATE`。凭证与会话文件保存在仓库外，目录与脚本不保存真实密码。

## 版本与交付

使用“候选 → 待核验 → 待脚本 → 待录制 → 待审阅 → 已完成”；需要修改时标记待更新，历史版标记归档。`episode.json` 的机器状态与此对应，待审阅使用 `needs-review`。

交付包含成片、独立字幕、配音、讲解稿和可继续制作的素材与脚本。记录适用产品版本；当前旧试片未记录精确产品提交号，按原始情况注明。用户审阅通过后再标记完成或创建发布标签。
