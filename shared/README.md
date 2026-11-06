# 公共素材

现已制作 [品牌风格 v0.1](brand/v0.1/README.md)：四组真实试音、30 秒样片、可编辑片头/图解/实操框架/片尾、视觉参数及生成脚本。用户已确认 C 读音与深蓝金色视觉，后续视频统一采用；当前基线入口为 brand/active.json。

N01 v3 与 N02 v2 均已采用已确认基线，新语境与整片核听仍待完成。产品图标保留来源，系统字体不复制分发。

- [当前基线](brand/active.json)、[产品发音配置](pronunciation.json)。
- [唯一基础样式](brand/v0.1/visual/base.css)、[公共可编辑模板](brand/v0.1/visual/template.html)。
- 品牌源配置与生成脚本在 brand/v0.1/source/，试听在 voice/，技术核验在 review/；用户确认状态在 source/review-status.json。
- A–D 试听是选择依据，C 是当前参考；保留候选以支持后续核对，不复制到各集整套素材。
- 各集通过 `node tools/capture-brand.cjs N01` 生成自己的画面；公共基线变化须先生成样片并审阅，不能默默改变既有视频。
