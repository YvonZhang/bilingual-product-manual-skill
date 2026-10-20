# v1.0.0 软件模板验收记录（历史）

日期：2026-10-20。范围：固定版式的中英文**软件操作手册**，可编辑 DOCX、PDF、逐页 PNG 与内部缺口报告。硬件彩页和规格书已在源材料分析中分流，未加入本技能。

本次本地验收通过。生成内容、产品、品牌、参数和示意界面全部虚构。原业务资料仅用于只读样式分析，未进入仓库。

## 验收矩阵

| 项目 | 实际结果 | 证据 |
| --- | --- | --- |
| 原样式提取 | 中英文各 16 个角色样式的段落/文字属性与参考一致；Letter、页边距和页眉页脚距离一致 | [样式契约](../bilingual-product-manual/references/style-contract.md)、[属性对照](style-fidelity.json) |
| 原样式目视对照 | 封面、目录、正文、步骤截图等模式已对照；原件与新样张的并排图仅本地保存，含原业务内容，未上传 | 样式契约记录固定项及有意差异 |
| 标准中英文生成 | 中文 5 页、英文 5 页，含表格、虚构截图、页眉页脚与目录；10 页全部打开目检通过 | [样张](../samples)、[自动检查](sample-qa.json)、[目检记录](visual-review.json) |
| 独立渲染复核 | 最终两份 DOCX 另用文档工具的标准渲染脚本导出；10 页尺寸及像素与技能渲染结果相同 | [渲染对照](canonical-render-comparison.json) |
| 长标题与长表格 | 中文 8 页、英文 6 页；长封面/目录/正文标题、54 行跨页表格、重复表头，无图片和品牌；14 页全部目检通过，54 行内容完整 | [边界自动检查](boundary-qa.json)、[目检记录](visual-review.json) |
| 缺字段和异常输入 | 16 项行为测试通过：缺英文、数值/单位/负号不一致、未解析事实、模板残留、无效来源、标题跳级、缺图片、路径越界、不完整或过高表格行、非适用模板等 | [测试日志](unit-tests.txt)、[测试代码](../bilingual-product-manual/tests/test_manual.py) |
| 独立从零调用 | 独立测试者只获得技能和新的原始虚构资料，自行整理 JSON；中文 4 页、英文 4 页，8 页全部目检，事实和限制条件核对通过 | [前向报告](forward-report.md)、[原始资料](forward-input/source.md)、[整理输入](forward-input/product.json) |
| 双语一致性 | 单一章节结构与共享 facts；自动检查数字/单位、标题/表格/图片数量；独立前向测试另核对否定、最大值、当前筛选结果等语义 | [前向自动检查](forward-qa.json)、[前向目检](forward-visual-review.json) |
| 无占位残留 | 标准、边界、独立前向输出均未发现模板标记；资料缺口只进入内部报告 | 三组自动检查 JSON |
| 路径可移植性 | 完整复制技能到含空格的新目录，改名，并从无关工作目录完成 build/render/check；不依赖本机绝对路径 | [搬迁测试](portability.json) |
| 技能结构 | 官方 quick_validate 校验通过；Python 编译检查通过 | 技能 frontmatter、文件与脚本结构检查 |
| 包内资料隔离 | 已核对文本/XML/PDF、原媒体哈希、原正文片段、作者元数据、凭据模式及本机路径；未发现命中 | [包内检查](package-scan.json) |
| 原件保护 | 10 份源成品前后 SHA-256 均相同；逐项原文件名及哈希仅本地保留 | 本地源文件保护记录 |

JSON 中的 `visual_review: required-separately` 是自动检查器的固定提示，不能由程序冒充目检结果。本次实际目检记录在本目录单独提供。

## 已修复的问题

1. 托管 LibreOffice 初次看不到已安装的中文字体，中文渲染缺字。增加临时 Fontconfig 字体发现和显式 `--font-dir`，没有安装字体或修改系统配置。
2. 长表格的行跨页拆分导致文本覆盖检查失败。增加行高上限校验与整行分页，保留重复表头；超高记录要求拆分内容，不能裁切。
3. 独立前向目检发现二级目录页码左移。统一右制表位后，使用同一输入重跑全部生成与目检；目录页正确，正文文本未改变。
4. 修复样式 ID 查找的弃用警告。最终独立构建及搬迁构建 stderr 为空。

## 复现

按技能 [README](../bilingual-product-manual/README.md) 准备 Python、LibreOffice、Poppler 和字体。在技能目录执行标准样例及单元测试：

```bash
python -m unittest discover -s tests -v
python scripts/manual.py build examples/fictional-product.json --out sample-output
python scripts/render.py sample-output
python scripts/check.py examples/fictional-product.json sample-output
```

独立前向输入与边界输入的复现命令见 [前向报告](forward-report.md) 和 `tests/make_boundary_case.py`。请在新的输出目录运行，并再次打开全部生成页检查。

## 尚未覆盖的环境与限制

- 验收环境为 macOS ARM64、Python 3.12.14、LibreOffice 25.2 托管构建；依赖版本已固定。没有在第二台实体电脑、Windows 或 Linux 完成运行测试，搬迁测试不能替代这些环境的验收。
- DOCX 为原生段落、文本、表格和图片，已校验其可编辑结构；未实际在桌面 Microsoft Word 中编辑。修改正文后必须更新目录和重新渲染。
- 字体不随包分发。更换字体或渲染器可能改变分页，不能承诺不同环境或不同内容像素完全相同。
- 数字和单位检查不能判断所有翻译语义，需结合原始资料核对。长表格是新增组件，不宣称源手册原有此组件。
- 包内扫描结合人工文件审阅使用，不是所有未知秘密的完备检测器。


当前硬件重点版本见 [v2 验收记录](report.md)。
