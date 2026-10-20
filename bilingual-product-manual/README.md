# 中英文产品手册技能 · v2.0.0

重点复用硬件中英文彩页与规格书的 A4 蓝白样式，同时保留独立的 Letter 黑白软件操作手册。硬件彩页输出原生文字/矢量 PDF；规格书和操作手册同时输出可编辑 DOCX 与 PDF。包内没有真实公司 Logo、联系方式、产品截图或业务正文。

## 安装与调用

将完整 `bilingual-product-manual` 目录复制到 Codex 的个人 skills 目录（通常为 `~/.codex/skills/`，或自定义 `CODEX_HOME` 下的 `skills/`）。不要只复制 `SKILL.md`；已有同名技能时先备份。新会话输入：

> 使用 $bilingual-product-manual，根据我提供的硬件资料生成中英文硬件彩页和产品规格书。保持模板版式，核对图片接口与参数。缺资料只记录在内部清单，不编造能力或认证。

软件调用可明确写“生成中英文软件操作手册”。两类输入、版式及脚本独立；无需先生成其他文档。

## 依赖与字体

- Python 3.10+。已验收 Python 包版本见 `requirements.txt`。
- 官方 LibreOffice 的 `soffice`、Poppler 的 `pdftoppm`，字体发现用 Fontconfig 的 `fc-match`。Codex 中优先使用工作区已加载运行时；脚本也查找 PATH，或接受明确的可执行文件路径。
- 硬件字体：Source Han Sans CN Regular/Bold（思源黑体 CN）。软件还使用 Arial、Courier New。字体不随包分发，请使用自己合法安装的字体；替代字体可能改变排版。
- 硬件可通过 `--font-regular` / `--font-bold` 指向安装的字体文件；渲染命令可多次指定 `--font-dir`。字体缺字会阻止构建，不能用替换方块冒充成功。
- 硬件 PDF 使用临时字形子集。CFF OTF 如需转换为 TrueType 轮廓，仅在临时目录处理当前文档所用字形，不向 skill 包写入字体。输入提供者应使用允许文档嵌入的字体。

自行管理的虚拟环境可安装可信来源依赖：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Windows 通常使用 `.venv\Scripts\python.exe`。不要向 Codex 托管依赖目录写文件。本次实际测试在 macOS ARM64，完成路径搬迁和含空格目录测试；未在第二台电脑、Windows 或 Linux 实测，目标机器应重新生成和验收。

## 从零试用硬件模板

从技能目录运行，使用新的输出目录：

```bash
python scripts/hardware.py validate examples/fictional-hardware.json
python scripts/hardware.py build examples/fictional-hardware.json --out hardware-output
python scripts/hardware.py render hardware-output
python scripts/hardware_check.py examples/fictional-hardware.json hardware-output
```

产生 `brochure-zh.pdf`、`brochure-en.pdf`、`specification-zh.docx`、`specification-en.docx`、规格书两份 PDF、所有页面 PNG、内部 `hardware-build-report.json`、自动 `hardware-qa-report.json`。样例产品、图像、所有参数与测试条件明确虚构。自动通过后仍需逐页打开 PNG 并核对资料。

完整说明见 [硬件输入约定](references/hardware-input-guide.md) 和 [样式契约](references/hardware-style-contract.md)。输入 `templates` 可只选择一种硬件文档。规格书可增加页数，彩页固定两页，过量内容必须显式编辑选择。

## 软件操作手册回归用法

```bash
python scripts/manual.py build examples/fictional-product.json --out software-output
python scripts/render.py software-output
python scripts/check.py examples/fictional-product.json software-output
```

得到中英 `manual` DOCX/PDF、逐页 PNG 和报告。渲染器只在输出副本更新目录缓存，不通过 LibreOffice 回存整个 DOCX。后续编辑后重新渲染/更新域。详见 [软件输入约定](references/input-guide.md)。

## 真实使用与分享边界

在自己的工作目录整理资料，按对应 schema 建立 JSON。图片相对于 JSON 寻址，禁止绝对路径和父目录跳转。脚本不下载图片、不读取凭据、不自动上传；使用本机字体发现和渲染进程。来源说明、缺口和构建报告可能包含内部内容，应留在本次工作区。

分享完整技能文件夹即可，或分享仓库中已经脱敏的样张。不要混入原资料、真实 Logo、截图或内部报告。源码复用许可由仓库所有者另行决定，本包不擅自给原品牌或源资料授予许可。维护验证用 `python -m unittest discover -s tests -v`，并执行独立资料端到端前向调用，不能只验证文件结构。
