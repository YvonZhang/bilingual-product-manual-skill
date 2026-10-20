---
name: bilingual-product-manual
description: 根据现有产品资料制作固定版式的中英文硬件彩页、硬件产品规格书或软件操作手册。硬件使用 A4 蓝白产品图、卖点场景和分组参数表；软件使用 Letter 黑白封面、目录及操作截图。输出 PDF，规格书和操作手册同时输出可编辑 DOCX，并进行完整渲染验收。
---

# Bilingual Product Manual · v2.0.0

先识别用户要求的文档种类，保留三种独立模板。硬件资料通常调用彩页和规格书两种；只有明确需要操作流程时才选软件手册，不擅自扩成整套文档平台。

| 模板 | 用途及样式 | 输出 |
| --- | --- | --- |
| `hardware-brochure` | A4 双页蓝白彩页，产品图、三项指标、场景、等高双栏参数和卖点卡片 | 中文、英文 PDF |
| `hardware-specification` | A4 蓝白规格书，产品概述、硬件与结构、分组参数、可选性能和功能应用 | 中文、英文 DOCX / PDF |
| `software-manual` | Letter 黑白封面、层级目录、操作步骤与截图、运行页眉和连续页码 | 中文、英文 DOCX / PDF |

## 从资料到输入

1. 只读本次资料。核实型号、版本、事实与来源之间的对应关系；冲突和缺失放入内部 `gaps`。不得从模板或历史产品继承能力、支持数量、参数、认证、默认口令或测试结果。
2. 硬件先读 [硬件输入约定](references/hardware-input-guide.md)、[硬件样式契约](references/hardware-style-contract.md)，建立符合 [硬件 schema](references/hardware-input.schema.json) 的 JSON。软件改用 [操作手册输入约定](references/input-guide.md)、[操作手册样式契约](references/style-contract.md) 与 [软件 schema](references/input.schema.json)。不要把两个输入模型混在一起。
3. 所有面向读者的文字提供 `zh` / `en`；共享数值及单位放在 `facts`，通过 `{{fact:id}}` 引用。两种语言引用同一事实。核对型号、版本、单位、比较方向、范围、限制条件、否定语义与术语；自动数字校验不能代替翻译语义审核。
4. 品牌、Logo、联系信息和产品图片来自用户授权输入，可全部省略。硬件图必须核对型号、接口种类及数量，并填写审核说明；发现图片与参数不符或未核对时停止该图的使用，解决冲突或经用户选择省略。不能复用历史不一致的例外。
5. 彩页通过显式 ID 选择卖点、场景和两栏参数；完整参数保留在规格书中。资料未支持性能指标时省略性能页；缺认证资料时不出现认证声明。无图片时采用纯文字区域，不画假产品、不留空占位框。
6. 测试资料一律 `fictional: true`，不得让虚构指标冒充真实能力。每项事实、参数、图片和营销段落记录来源 ID；原文件路径和内部资料不加入分享包。

## 生成

在独立工作目录准备输入与相对路径图片，输出使用新目录。脚本以自身位置寻找模板，可从任意目录调用。Python、字体、渲染器安装和完整示例见 [README](README.md)。

硬件：

```bash
python scripts/hardware.py validate /path/to/hardware.json
python scripts/hardware.py build /path/to/hardware.json --out /path/to/new-output
python scripts/hardware.py render /path/to/new-output
python scripts/hardware_check.py /path/to/hardware.json /path/to/new-output
```

软件：

```bash
python scripts/manual.py validate /path/to/product.json
python scripts/manual.py build /path/to/product.json --out /path/to/new-output
python scripts/render.py /path/to/new-output
python scripts/check.py /path/to/product.json /path/to/new-output
```

硬件彩页是两页的编辑设计，溢出会明确失败。通过较短 `meta.short_title`、精炼有来源的文案或减少显式彩页选项解决；不能静默删参数、改数值或缩小字号。规格书允许自然增加页数，长表重复表头、整行跨页，不保证两种语言总页数相同。操作手册渲染器按实际分页回填目录缓存并再次核验。

## 验收与交付

逐页打开所有 PNG，检查缺字、标题、图像比例、页眉页脚、参数表行高、留白与跨页；硬件还要检查彩页双栏底部一致、四份文件 Logo 可见宽度一致、图片接口与参数一致；软件检查目录页码和图注。检查实际 PDF 的全文覆盖、数值单位和模板标记，不能仅用结构校验宣告完成。

遇到问题，修改资料或明确的布局规则，在新输出目录重建。不同字体、操作系统或渲染器可能改变分页，需重新验收；不得承诺未经测试的像素一致或跨系统成功。

交付用户选择的中英成品、可编辑文件、内部缺口清单和实际验收结果。`gaps` 仅保存在内部构建报告，读者文件中不留下模板占位。保护原件；本技能不自动上传、发送或发布。

维护时运行 `python -m unittest discover -s tests -v`，再从独立产品原始资料执行一次完整前向测试，并保留其他模板回归结果。
