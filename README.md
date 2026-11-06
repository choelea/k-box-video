# 问学知识平台 · 视频系列

**问学是上位品牌；K-BOX / 问学知识平台是旗下的一个产品。** 本仓库统一维护该产品的视频选题、制作规范、素材、成片和发布说明。正式教程每集 2–7 分钟。

## 从哪里开始

| 要做什么 | 入口 |
| --- | --- |
| 讨论内容范围 | [内容主线](planning/K-BOX视频系列-内容主线规划.md) |
| 选择分类和题目 | [分类与选题](planning/K-BOX视频系列-分类与选题规划.md)：N 认知、T 任务、S 细节、R 诊断，当前 50 个编号主题 |
| 制作或修改视频 | [制作与修改](standards/制作与修改.md)、[验收标准](standards/验收标准.md) |
| 使用统一品牌与版式 | [品牌与发音](standards/品牌与发音.md)、[视觉风格](standards/视觉风格.md)、[公共素材](shared/README.md) |
| 新建一集 | [选题卡](templates/episode/选题卡.md)、[分镜模板](templates/episode/分镜.md)、[目录规则](standards/目录与版本管理.md) |
| 将视频放入官网 | [接入与发布说明](distribution/产品官网-首页介绍视频.md) |
| 检查重复和资料完整性 | [整理结果与后续规划](reports/目录整理与后续规划.md)、[机器检查报告](reports/repository-audit.json) |
| 找回旧版本 | [历史版本恢复记录](reports/history/历史版本.json) |

## 当前视频

| 编号 | 内容与状态 | 交付与源文件 |
| --- | --- | --- |
| N01 | 基础介绍 v3，3:52；已更新文档中心，纠正品牌与产品层级，新语境与整片待核听 | [完整项目](episodes/N01/README.md)、[MP4](episodes/N01/问学知识平台-基础介绍.mp4)、[字幕](episodes/N01/问学知识平台-基础介绍.srt)、[配音](episodes/N01/问学知识平台-中文配音.mp3)、[讲解稿](episodes/N01/讲解稿.md) |
| N02 | 企业场景版 v2，4:32；售后质量问题跨制度检索与核验，两处产品简称待纠正 | [完整项目](episodes/N02/README.md)、[场景方案](episodes/N02/场景方案.md)、[MP4](episodes/N02/N02-企业场景版.mp4)、[字幕](episodes/N02/N02-企业场景版.srt)、[配音](episodes/N02/N02-企业场景版-配音.mp3)、[讲解稿](episodes/N02/讲解稿.md) |

技术检查通过与用户内容审阅分别记录，具体待办以各集 `episode.json` 为准。本次目录整理沿用当前讲解与演示内容。

## 目录分工

```text
planning/             系列内容范围、分类与选题；单集场景放在单集目录
standards/            制作、命名、发音、视觉、验收和版本管理规则
shared/               公共品牌基线、发音参考和共享视觉样式
templates/episode/    新集选题卡、分镜和元数据模板
episodes/<编号>/      每集当前版本、源文件、原始素材与验收资料
distribution/         官网等渠道的接入、发布与更新说明
reports/              全仓检查结果、整理规划；history/ 保存迁移及恢复记录
tools/                全仓共用的检查、合成入口、截图与试看工具
```

不再维护 `archive/` 目录副本。旧成片与完整旧项目通过 Git 历史及 Git LFS 恢复。`k-box-docs` 仅保留视频资料入口，产品音视频解析等设计仍在产品文档仓库。

## 安装与常用命令

需要 Python 3.11+、Git LFS、FFmpeg/ffprobe（含 libass）。当前使用 macOS 苹方字体；其他系统须配置有授权的中文字体并复核版式。重新截图还需要 `npm install` 和 Chrome，`CHROME_PATH` 可覆盖公共截图工具的浏览器路径。

```bash
git lfs install --local
git lfs pull
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# 只检查，不访问线上系统，不调用语音服务
.venv/bin/python tools/audit.py --output reports/repository-audit.json
.venv/bin/python tools/video.py check N01
.venv/bin/python tools/video.py check N02
.venv/bin/python episodes/N01/source/narrate.py --check-only

# 使用现有配音与原始素材离线导出
.venv/bin/python tools/video.py render N01

# 复用公共样式，从本集 scenes.json 生成品牌画面
node tools/capture-brand.cjs N01

# 单集试看；共享品牌图标等资源时从仓库根目录提供服务
.venv/bin/python tools/serve.py . --port 8770
```

仓库根目录试看入口为 `/episodes/N01/试看.html` 和 `/episodes/N02/试看.html`。`tools/video.py serve N01 --port 8769` 也可服务单集，但引用仓库公共素材的页面宜用根目录服务。

`render` 不自动重做配音、截图或线上问答。改讲解文本时同步 `source/speech-overrides.json`，生成后核对时间线和镜头，再导出；未列入覆盖表的现存配音通过 `source/narration-manifest.json` 校验，防止只改文本而复用旧声音。

重新录制需通过仓库外环境变量提供登录状态。账号、Token 和浏览器会话不入库。视频、音频和位图走 Git LFS；`build/` 是本地可再生缓存，可清理，不能存放唯一原素材。
