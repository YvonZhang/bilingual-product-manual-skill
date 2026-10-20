# 硬件输入约定

`hardware.py` 接受一个 UTF-8 JSON，文件和图片留在用户自己的资料目录。完整且明确虚构的例子见 `examples/fictional-hardware.json`；机器字段定义见 `hardware-input.schema.json`。脚本还检查来源 ID、引用关系、数字单位、图片文件和排版容量，JSON schema 校验不能替代这些检查。

## 文档选择

`templates` 是非空数组，可选 `hardware-brochure`、`hardware-specification` 或两者。软件操作手册用另外的 `template: software-manual` 模型和 `manual.py`。

| 字段 | 必需 | 含义 |
| --- | --- | --- |
| `schema_version` | 是 | 当前为 1；它是输入结构版本，不是 skill 版本 |
| `meta` | 是 | 双语正式产品名、概述，以及共享型号、资料版本、来源；可有短彩页标题、副标题、订货说明 |
| `sources` | 是 | 来源 ID 和简短说明；路径、保密细节不进入分享包 |
| `facts` | 有数值时 | 共享事实字典，每个值包括字符串 `value`、可选 `unit` 和 `sources` |
| `spec_groups` | 是 | 分组标题及完整参数行；行包含唯一 ID、双语名称、双语值、来源 |
| `metrics` | 否 | 最多三项大数字指标，引用 `facts`；没有已核实指标就省略 |
| `features` / `applications` | 否 | 带唯一 ID、标题、说明和来源的功能/应用场景 |
| `performance` | 否 | 有来源、说明、条件的性能表；无证据则整个字段省略 |
| `brochure` | 选彩页时 | 独立营销短文、两个非空参数 ID 列表、显式选择的功能/场景 ID |
| `brand` / `images` | 否 | 本次品牌与图片；不包含默认真实资产 |
| `gaps` | 否 | 内部缺口，动作 `omit` 或 `internal`；不会写到读者文件 |
| `theme` | 否 | 字体、五种颜色、可见 Logo 宽度，其他几何规则保持固定 |

所有双语对象必须同时有 `zh`、`en` 非空值。不要把另一种语言的空字段自动复制。数值和单位只维护一次：

```json
{
  "facts": {
    "mass": {"value": "0.48", "unit": "kg", "sources": ["brief"]}
  },
  "value": {"zh": "{{fact:mass}}", "en": "{{fact:mass}}"}
}
```

以上是字段片段，不是完整输入，也不声明真实产品重量。两种语言必须引用相同事实 ID；数字、已知单位、比较符号会校验。汉字单位、否定语义、试验条件、营销表达仍需人工审核。品牌联系方式等共享字符串不能在翻译时替换为另一个组织。

## 图片和品牌

`brand.logo` 及图片路径相对于 JSON 目录，仅接受 PNG/JPEG；禁止绝对路径、父目录跳转及越界符号链接。生成器不联网下载资源。Logo 会在临时副本去除透明/纯白外围空白，按默认 28 mm 可见宽度使用；横向标志高度不能超过 29 pt。不要修改源图片来让错误接口看起来符合参数。

每张 `images.hero`、`images.detail` 必须提供：

- `path`、与 `meta.model` 一致的 `model`、`sources`。
- `interface_check: matched`：核对图片中的实际接口类型、数量与本次参数一致；`not_applicable` 仅用于确实未显示可核对接口的照片，并在说明中解释。
- 双语 `review_notes`，记录本次核对结论；可选双语 `caption`。

标记 `mismatch` 或 `unverified` 会被拒绝。脚本无法看懂照片、证明用户填写的审核结论真实，必须由调用者视觉核验。省略 `images` 时规格书删除图片段、彩页使用全宽文案；无 Logo/联系人时不留模板标记。

## 彩页容量与规格书长表

彩页固定两页。`parameter_columns` 中每个 ID 必须来自完整参数表且不能重复；两栏按照两种语言所需最大高度分配，默认总高 244 pt，最多 260 pt。`feature_ids` / `application_ids` 各最多四项，可以为空。生成器不会自行挑选或丢弃参数。

`meta.short_title` 只替换彩页标题，规格书保留 `meta.product`。两行以内短标题更接近参考版式。过长标题/卡片/参数会返回清楚错误，需在不改变事实的前提下编辑短文。完整正式产品名在规格书最多三行，超长时需由资料所有者明确适用正式名称。

规格书参数可自然跨页，重复表头，不把同一记录分在两页；双语最小行高按较长语言估算。超长单条记录需拆成多个有意义的独立记录。不能设置固定行高来裁掉文字。缺少性能条件时不能生成性能表。无性能页时标准样例从四页降为三页，页数不作为事实完整性的替代指标。

## 内部缺口与交付

例如 `gaps: [{"field":"certifications","reason":"No evidence supplied","action":"omit"}]`。这条内部说明不会成为认证声明。`hardware-build-report.json` 含输入事实、缺口、文字与排版报告，可能含用户内部内容，分享前由用户决定范围。普通交付为两份彩页 PDF、两份规格书 DOCX/PDF，或其中用户选择的类别。
