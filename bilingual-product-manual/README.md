# 中英文软件操作手册技能

将现有产品资料整理成固定版式的中英文 DOCX/PDF。模板保留 Letter 纸张、黑白标题、双层目录、灰色图注、运行页眉和连续页码。包内没有真实公司 Logo、联系方式、产品截图或业务正文。

这是可分享的普通 Codex skill，未注册为 Template Gallery 的 artifact-template，也不包含硬件彩页或规格书模板。

## 安装

把整个 `bilingual-product-manual` 文件夹复制到 Codex 的个人技能目录（通常为 `~/.codex/skills/`，或自定义 `CODEX_HOME` 下的 `skills/`）。不要只复制 `SKILL.md`。已存在同名技能时先备份或选择独立安装位置，不直接覆盖。

在新会话输入：

> 使用 $bilingual-product-manual，根据我提供的产品说明、功能流程和截图生成中英文用户操作手册。产品版本为本次资料标明的版本，缺资料处记录在内部清单，不编造。

脚本也可脱离 Codex 单独使用。示例命令中的 `python` 指目标环境中的 Python 3.10 或更高版本。在 Codex 里优先使用工作区依赖加载工具给出的 Python；不要在托管依赖目录安装或写文件。

## 依赖

- Python：`python-docx`、`lxml`、`Pillow`、`pypdf`，已验收版本见 `requirements.txt`。
- PDF：官方 LibreOffice 的 `soffice` 与 Poppler 的 `pdftoppm`。Codex 环境自动优先查找同一运行时中的程序；其他环境使用 PATH，或传入 `--soffice`、`--pdftoppm` 的实际路径。
- 字体：Arial、Source Han Sans CN（思源黑体 CN）、Courier New。字体不随包分发。请使用自己的合法字体或在 `theme.fonts` 中选择已安装替代字体；替代字体可能改变分页。
- 如有 `fc-match`，脚本会发现字体目录并检查字体名称。没有该命令时使用多次 `--font-dir`，分别传入实际拉丁文和中文字体目录。字体配置只写入临时目录，不修改系统配置。

需要手动安装 Python 依赖时，在自己管理的虚拟环境使用可信包索引：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Windows 的虚拟环境解释器通常为 `.venv\Scripts\python.exe`。本包未实际在 Windows 或 Linux 完成渲染验收；跨平台支持需要在目标机器验证。

## 从零试用

在技能文件夹内运行，输出目录必须尚未包含同名 DOCX：

```bash
python scripts/manual.py build examples/fictional-product.json --out sample-output
python scripts/render.py sample-output
python scripts/check.py examples/fictional-product.json sample-output
```

示例产品、参数和界面均为虚构。成功后得到 `manual-zh.docx`、`manual-en.docx`、两个 PDF、逐页 PNG、`build-report.json` 与 `qa-report.json`。自动 QA 通过后，仍需逐页目检。

真实调用先复制示例 JSON 到自己的资料目录，再替换为本次证据支持的内容。图片相对于该 JSON 所在目录寻址；不得使用绝对路径或 `..`。生成器不会下载外部资源。

`render.py` 只在新输出副本中更新目录缓存，不用 LibreOffice 回存整个 DOCX；页面与标题样式保持可编辑。后续在 Word 中修改内容后需要重新渲染/更新域，以免目录页码过期。

## 分享边界

分享此文件夹即可；不要把自己的 `product.json`、原始资料、Logo、截图或生成的内部报告混入公共技能包。样式模板无正文，测试样例清楚标注虚构。发布 GitHub 的仓库与可见范围应由发布者确定。此包没有设置自动上传，也没有读取凭据的代码。

不随包分发第三方字体或品牌资产；其使用权由输入提供者管理。源码复用许可由仓库所有者另行决定，本包不擅自给原品牌或源资料授予许可。
