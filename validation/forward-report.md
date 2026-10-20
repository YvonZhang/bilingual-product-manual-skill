# 独立前向测试

测试日期：2026-10-20。测试者为未参与技能实现的独立代理。只提供最终技能的位置、独立原始虚构资料、可用运行时和独立输出目录；没有提供预期版面、答案或实现提示。

测试者阅读技能后，从 [原始资料](forward-input/source.md) 自行整理 [product.json](forward-input/product.json)，执行 `validate → build → render → check`，实际打开每张页面图片，再核对原资料语义。产品为完全虚构的 Cedar Queue Workbench，版本 0.7.2；没有 Logo、截图、联系方式、认证、固定密码或系统要求，因此没有添加这些内容。

首轮发现二级目录页码右对齐问题和样式查找弃用警告。实现修复后，测试者使用**完全相同的输入**重新完成四步流程与全部 8 页目检。最终命令均退出 0、stderr 为空；未修改技能源码来使测试通过。

| 项目 | 最终结果 |
| --- | --- |
| 中文 / 英文 | 各 4 页，全部目检通过 |
| 原生结构 | 每份 45 个段落、68 个文本 run、1 个表格、0 张图片 |
| 双语章节结构 | 各 7 个标题，完全匹配 |
| 事实语义 | 每 20 s 刷新、最多保留 150 张、单次最多导出 25 张、导出当前筛选结果、Reset 清空筛选、保存后出现在队列顶部，均一致 |
| 资料缺口 | 6 项，只在内部报告中记录 |
| 修复回归 | 正文文本与首轮完全相同；第 1、3、4 页像素相同，仅第 2 页目录对齐按预期变化 |
| 遗留阻塞 | 无 |

证据：[自动检查](forward-qa.json)、[逐页目检](forward-visual-review.json)、[回归对照](forward-regression.json)。不上传含本机路径的运行日志或原产品资料。

从仓库根目录复现（输出目录需为新目录）：

```bash
python bilingual-product-manual/scripts/manual.py validate validation/forward-input/product.json
python bilingual-product-manual/scripts/manual.py build validation/forward-input/product.json --out forward-output
python bilingual-product-manual/scripts/render.py forward-output
python bilingual-product-manual/scripts/check.py validation/forward-input/product.json forward-output
```

本次独立输入没有图片或跨页表格；这些组件由主任务的标准和边界样例另行测试。独立测试未覆盖其他操作系统。
