---
name: bilingual-product-manual
description: 根据现有产品资料生成固定版式的中英文软件操作手册，输出可编辑 DOCX 和经渲染检查的 PDF。适用于复用黑白封面、分级目录、步骤与截图排版；不用于硬件彩页或规格书。
---

# Bilingual Product Manual

把用户提供的资料整理成同一版式的中文、英文软件操作手册。先读
[输入约定](references/input-guide.md) 和 [样式契约](references/style-contract.md)。
本技能含两份无产品正文的 DOCX 样式模板；所有产品事实、品牌和图片均来自本次输入。

## 内容准备

1. 只读用户资料，区分操作流程、系统要求、参数、界面名称和资料缺口。优先使用与目标版本一致的材料；遇到冲突记录来源并请用户明确，不能从样式示例或旧产品继承能力。
2. 根据实际功能组织章节。典型结构是简介、使用准备、快速入门、操作说明；没有资料的可选章节省略。不得为凑齐章节编写能力、支持路数、认证、默认口令或操作步骤。
3. 在独立输出工作目录建立 `product.json`，符合 [input.schema.json](references/input.schema.json)。每个内容块和事实均填写来源 ID；原始文件路径留在本次工作区，不复制进技能目录。
4. 统一维护一套章节 ID 和 `zh` / `en` 字段。将数值和单位写成共享 `facts`，正文引用 `{{fact:id}}`。保持数字、版本、型号、限制条件、否定语义和界面操作一致；术语表由本次资料形成，不能套用示例产品术语。
5. 使用用户提供且可使用的 Logo、联系方式和截图。没有图片时省略 figure，不插空框、不生成冒充真实产品的界面。测试资料必须设置 `fictional: true`；随包示例全部虚构。

## 生成与验收

从技能根目录运行；也可以使用脚本的绝对路径，脚本以自身位置寻找模板，不依赖当前目录。
在 Codex 中优先使用已加载的工作区 Python、LibreOffice 和 Poppler。依赖与字体说明见
[运行与安装](README.md)。不能在依赖管理目录中写输出。

```bash
python scripts/manual.py validate /path/to/product.json
python scripts/manual.py build /path/to/product.json --out /path/to/new-output
python scripts/render.py /path/to/new-output
python scripts/check.py /path/to/product.json /path/to/new-output
```

`render.py` 会使用独立临时渲染配置，检查字体、导出 PDF 和每页 PNG，并根据实际分页回填 DOCX 目录缓存，再次渲染直到页码稳定。不要使用未渲染的 DOCX 宣布完成。

逐页打开 `pages-zh`、`pages-en` 的 PNG，检查封面换行、中文缺字、页眉、页脚、目录页码、标题与下文关系、表格跨页重复表头、图片图注及末页。结合原资料检查两种语言的事实、语义和单位；数字校验不能替代语义核对。缺字时先修复字体可见性，勿用删除中文来通过测试。

发现问题后修改输入或明确的排版规则，在新的输出目录重新生成、渲染和校验。标记每个已通过/未通过项，且只描述实际完成的验证。操作系统、字体或渲染器变化会改变分页，需重跑验收；不承诺像素完全相同。

交付两份 DOCX、两份 PDF、内部资料缺口和简短验收结果。PNG 与测试日志按用户需要提供。保留原件。技能调用不包含上传、发送或发布权限。

## 范围与扩展

- 只提供 `software-manual`。硬件彩页和规格书不是该模板的可选配色；需要另行分析其版式后独立制作，不能偷换结构。
- 固定底层纸张、字体层级和段距。品牌名、Logo、字体替代、有限颜色与目录层级可配置。更改字体必须重新验收。
- 表格是为操作手册参数与重复记录补充的组件，原参考手册以步骤和截图为主。没有来源支持的参数行不得生成。
- 长标题可以通过 `meta.title` 提供较短封面标题，`meta.short_title` 提供页眉标题；正文保留完整正式名称。不能静默缩小字体来塞入长文本。
- `gaps` 仅进入内部 `build-report.json`。必要事实缺失应补齐后生成；非必要资料省略并记录，不能在面向读者的手册中留下模板标记。

维护脚本时运行 `python -m unittest discover -s tests -v`，再用独立产品资料做端到端生成和目检。结构校验不等于前向调用成功。
