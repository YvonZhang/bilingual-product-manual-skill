# 输入约定

JSON 是从原材料中提炼的中间数据，不要求最终用户手工编写；Codex 应从用户的 PDF、DOCX、说明文字和截图整理出来。用户原材料仍是事实来源，示例只示范结构。

## 最小结构

- `schema_version: 1` 与 `template: "software-manual"`。
- `meta.product`、`meta.intro`：含非空 `zh` 和 `en`；`meta.version` 是共用字符串。
- `sources`：唯一来源 ID、说明；可描述文件名和页码，不要把私有绝对路径写进公开包。
- `sections`：按阅读顺序排列；每节有 `id`、`level`、双语 `title`、`blocks`。
- 内容块：`paragraph`、`step`、`note`、`code` 使用双语 `text`；`figure` 使用相对 `path`、双语 `caption`/`alt`；`table` 使用双语 headers 和 rows。
- 每个内容块与 fact 的 `sources` 必须引用已定义来源。记录来源只能证明整理过程可追溯，仍需人工核对其是否真正支持陈述。

示例见 [fictional-product.json](../examples/fictional-product.json)。完整机器可读结构见 [input.schema.json](input.schema.json)。运行时的输入校验还检查章节顺序、数值、单位、资产路径和来源引用。

## 事实与翻译

`facts` 的每项由 `value`、可选的 `unit` 和来源 ID 构成。value 必须为字符串，以保留小数精度、版本或型号。一个事实只写一次，例如：

```json
"refresh_interval": {"value": "15", "unit": "s", "sources": ["user-guide"]}
```

两种语言的文字都引用 `{{fact:refresh_interval}}`；生成后都是 `15 s`。不要在中文写 15、英文手填 30。单位使用同一写法；需要换算时先明确原始值、条件和单位，再由资料负责人确认。校验会拒绝数字不同、常用单位不同、缺译或残留模板标记。

数字匹配无法判断主语、否定、条件是否翻译正确。最终双语核对必须检查这些内容，并核对按钮名称与实际截图。界面只有英文时，中文可写“保存（Save）”，英文写“Save”。有双语截图时，`figure.path` 可以是 `{"zh":"images/zh.png","en":"images/en.png"}`；同一个编号仍对应同一操作。

## 可选配置

- `meta.title`：短封面标题；未提供时自动在产品名后添加用户手册类型。
- `meta.short_title`：短运行页眉，最长 90 字符；完整产品名称可保留在简介。
- `meta.applies_to`：资料中明确的适用范围。
- `brand.name`、`brand.contact`：双语字符串；`brand.logo` 为相对图片路径。未提供则不显示。
- `theme.fonts`：latin、cjk、code；颜色仅可改 text_color、caption_color、table_header_fill、table_border；`toc_depth` 为 1 或 2。
- `section.page_break: true`：该节从新页开始。短简介和使用准备可共页。
- `table.widths`：列宽的正数权重。表格 2..6 列，单元格过长时拆记录或改为正文。
- `gaps`：field、reason、action（omit 或 internal）。不会出现在正文。

不可把 `gaps` 当成所有不确定事实的免责条款。版本、名称或关键操作步骤缺失时先补齐；非适用章节应省略。输入中的缺口不是模板占位符，不应带着 `TODO`、`TBD` 或 `[[...]]` 发布。

## 图片与边界

图片需位于 JSON 的目录或其子目录。拒绝绝对路径、向上跳转和越界符号链接。支持 PNG/JPEG，不下载链接。未提供截图时不要加入 figure；提供了不存在的截图则报错，避免悄悄漏图。

虚构测试设置 `fictional: true`，并将来源标记 fictional；输出封面会明确标注。真实任务不要复制测试参数或测试品牌。
