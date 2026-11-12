# N04 · 企业 Wiki 怎样把分散资料变成可阅读知识？

> **编号**: N04  
> **分类**: 认知与选型  
> **预计时长**: 3-4 分钟  
> **状态**: 脚本编写完成，待截图和配音

## 视频简介

本视频深入讲解企业 Wiki 的核心能力：如何自动将分散在多份文档中的知识，聚合成结构化的主题页面。通过演示环境展示 Wiki 的工作流程，包括源文档上传、自动生成主题页面、来源追溯和智能问答。

**重要说明**：本视频使用演示数据，非真实业务数据。

## 章节结构

| 章节 | 时长 | 内容 |
|------|------|------|
| intro | ~9s | 开场介绍 |
| problem | ~16s | 业务痛点：资料分散、知识难沉淀 |
| solution | ~22s | 解决方案：自动聚合、主题沉淀 |
| demo-overview | ~12s | 演示环境说明（标注演示数据） |
| demo-sources | ~15s | 源资料展示 |
| demo-pages | ~22s | 生成的主题页面 |
| demo-trace | ~16s | 来源追溯特性 |
| demo-qa | ~14s | Wiki 问答演示 |
| value | ~23s | 业务价值和适用场景 |
| comparison | ~29s | Wiki vs 文档问答的区别 |
| outro | ~14s | 小结 |

## 文件结构

```
N04/
├── source/
│   ├── plan.json              # 讲解稿结构
│   ├── timeline.json          # 时间线配置
│   ├── brand-with-logo.html   # 品牌幻灯片
│   ├── demo-ui.html           # 演示UI截图源
│   ├── capture.cjs            # 截图捕获脚本
│   └── assemble.py            # 视频合成脚本
├── frames/                    # 截图输出目录
├── audio/                     # 配音文件
├── temp/                      # 临时文件
├── review/                    # 审阅资料
├── episode.json               # 集数元数据
└── README.md                  # 本文件
```

## 制作步骤

### 1. 捕获截图

```bash
cd episodes/N04
node source/capture.cjs
```

将生成品牌页面和演示UI截图到 `frames/` 目录。

### 2. 生成配音

使用语音服务根据 `source/plan.json` 生成配音，保存到 `audio/narration.wav`。

### 3. 合成视频

```bash
python source/assemble.py
```

将生成 `N04-企业Wiki知识沉淀.mp4`。

## 演示数据说明

本视频使用模拟的产品界面截图，展示：
- Wiki 库的源文档列表
- 自动生成的主题页面
- 页面详情和来源追溯
- Wiki 问答对话

所有数据均为虚构，仅用于说明产品能力。截图右上角标注"演示数据 · DEMO"。

## 关联视频

- **N01**: 问学知识平台基础介绍
- **N02**: 企业场景版
- **N03**: 四种知识能力怎么选（选型框架）
- **T03**: 从分散资料到可阅读、可问答的企业 Wiki（任务实操）

## 内容来源

基于 K-BOX 产品文档：
- [知识库类型](../../../k-box/k-box-wiki/docs/features/knowledge-base-types.md)
- [Wiki 库快速开始](../../../k-box/k-box-wiki/docs/features/quick-start/quick-start-wiki.md)
- [Wiki 设计文档](../../../k-box/k-box-docs/概要设计/Wiki/)
