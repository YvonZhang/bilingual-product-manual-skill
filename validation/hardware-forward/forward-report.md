# 独立硬件前向验证报告

**最终结论：修复后通过。** 以新提供的虚构“栖木标签核对器 / Perch Label Checker”资料，从零建立双语输入，生成中英文硬件彩页和规格书。四份 PDF 共 10 页，全部实际打开目检通过；两份规格书 DOCX 保持原生可编辑。两类故意错误输入均明确拒绝。没有剩余失败项或执行阻塞。

## 独立性与实际过程

只读取目标技能的 SKILL、README、硬件约定/schema 和脚本，未读取或复用包内硬件示例事实。将本次原始资料保存为 [source.md](source.md)，独立建立 [hardware.json](hardware.json)：11 个共享事实、3 组 9 行完整参数、3 项指标、2 项演示功能、2 个场景及 7 项内部缺口。

首轮与修订版均实际执行 `validate → build → render → check`。主任务修复后以**同一份输入、相同内容**在新目录 `output-final` 完整重跑，没有通过缩短文案、删除参数或重复版本行迁就代码。两轮生成命令都退出 0；正常输入及最终生成/渲染/检查 stderr 均为空。命令、返回码和输出保存在 [执行摘要](execution-summary.json)。

使用指定的运行时 Python 3.12.14、脚本自动选择的同一运行时 LibreOffice/Poppler，以及允许的私有 `hardware-deps` 路径中的 fonttools 4.60.1。没有安装依赖、修改生产文件、操作远端或上传 GitHub。输入 SHA-256 两轮一致：`db83af46e6213369335d107022b11a7c1d2a05ff254e1d65f8e90dc776dca176`。

## 最终产物

| 类型 | 中文 | 英文 | 页数 |
| --- | --- | --- | --- |
| 硬件彩页 | [PDF](output-final/brochure-zh.pdf) | [PDF](output-final/brochure-en.pdf) | 各 2 页 |
| 硬件规格书 | [DOCX](output-final/specification-zh.docx) / [PDF](output-final/specification-zh.pdf) | [DOCX](output-final/specification-en.docx) / [PDF](output-final/specification-en.pdf) | 各 3 页 |

逐页 PNG 留在本地测试工作区；本包保留成品和逐页检查记录。每份规格书有 51 个原生段落、51 个文字 run、5 个原生表格，无图片/media/customXml；表头可重复、记录不拆页、行高不是固定裁切值。彩页为原生文字和矢量图形，所有 PDF 页面图像对象数为 0。自动检查见 [hardware-qa-report.json](output-final/hardware-qa-report.json)，内部缺口见 [本次输入](hardware.json) 的 `gaps`。

## 实际发现与修复

1. **独立发现：资料版本静默遗漏。** 首轮 `meta.version: 0.3.0` 完全未出现在四份 PDF 中，自动 QA 却通过。已保留 [首轮全文证据](extracted-text-evidence.json)；首轮产物和完整日志留在本地测试工作区。主任务修复为页眉显示“资料版本 / Revision”，并新增版本覆盖检查；最终 10 页均有 `0.3.0`，实际目检和全文提取均确认。
2. **主任务发现，独立回归确认：规格书页眉居中。** 首轮确实可见文档类型位于页眉中部。主任务清除继承的默认居中制表位后，最终页眉文档类型对齐右边缘约 559.3 pt，全部页面目检通过。
3. **前置环境说明：** 主任务在我第一次 build 前已清理规格书样式模板的 customXml/默认缩略图。此项未造成我的实际失败，不能算成本代理复现的问题。

本代理没有做生产修复，也没有修改有效输入；完成调用所做的环境配置仅为指定 `PYTHONPATH` 指向已授权的私有依赖目录。

## 拒绝测试

| 故意错误 | 首轮及最终版本结果 |
| --- | --- |
| 重量中文 `0.22 kg`、英文 `0.22 g` | 均退出 2：`row.value: bilingual hardware unit mismatch` |
| 删除 `meta.overview.en` | 均退出 2：`meta.overview: missing fields ['en']` |

原错误输入保留为 [invalid-unit.json](invalid-unit.json)、[invalid-missing-english.json](invalid-missing-english.json)，仅运行校验，没有生成这些错误版本的读者文档。

## 逐页目检与语义核对

中英彩页第 1 页的标题、培训模拟范围、3 / 24 / 120 s 指标及两个场景通过；第 2 页的 9 项参数、双栏共同底线 564 pt、功能卡片通过。中英规格书第 1 页的概述和指标，第 2 页的三个参数组，第 3 页的两项功能与两种场景全部通过。所有 10 页的版本、型号、页眉、页码及末页检查通过，无缺字、重叠、溢出、占位图或不完整记录。详细逐页记录见 [visual-review-final.json](visual-review-final.json)。

已逐项核对：3 处检查位、单次 24 张、64 MB、120 s、9 V DC / 1 A、示例功耗 4 W、110 × 70 × 25 mm、0.22 kg、10 °C 至 35 °C。保留“仅供培训模拟”“只演示顺序核对与状态清除”及“示例功耗”限定，没有加入扫描识别、联网、认证、性能测试或准确率声明。

没有原样例产品、品牌、Logo 或联系人残留。除目检外，将 PDF 全文与本次读者字段、共享事实、型号版本及中性模板标题逐项匹配，未发现多余词语或品牌文字；两份 DOCX 无媒体。见 [final-evidence.json](final-evidence.json)。

本次无图、无 Logo，因此未验证接口图片审查或 Logo 等宽；表格未跨页，未目检跨页续表；未验证其他操作系统。以上是覆盖边界，不是当前请求的失败项。
