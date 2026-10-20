"""Write a fictional long-title, long-table case without brand or images."""
import argparse,json
from pathlib import Path

def create(dest):
    pair=lambda z,e:{'zh':z,'en':e}
    src=['boundary-fixture']
    rows=[]
    for i in range(1,55):
        rows.append([pair(f'记录 {i}',f'Record {i}'),pair(f'虚构的第 {i} 项检查记录，包含足够长的说明，以验证自动换行和表格跨页后内容是否完整。',f'Fictional inspection record {i}, with a deliberately long description to verify text wrapping and complete content after the table crosses a page boundary.')])
    d={'schema_version':1,'template':'software-manual','fictional':True,
       'meta':{'product':pair('用于验证长标题与多页记录表排版的虚构产品工作台','Fictional workbench for testing long headings and multipage record tables'),
       'title':pair('用于检查跨团队工作流程中长标题换行与多页资料表格的虚构产品工作台用户操作手册','User Manual for a Fictional Workbench That Tests Long Titles and Multipage Record Tables Across Detailed Team Workflows'),
       'short_title':pair('虚构边界测试工作台','Fictional Boundary Workbench'),'version':'0.1.0',
       'intro':pair('本手册是虚构的边界测试，验证长标题、长表格、缺少品牌和没有图片的情况。','This fictional boundary test checks long titles, long tables, omitted brand details, and a manual without images.')},
       'sources':[{'id':src[0],'description':'Entirely fictional boundary-test input.','fictional':True}],
       'sections':[{'id':'long-title','level':1,'title':pair('跨团队工作流程中的长标题换行与多页资料表格完整性检查操作说明','Operating Instructions for Checking Long Heading Wrapping and Multipage Record Table Completeness Across Team Workflows'),
       'blocks':[{'type':'paragraph','text':pair('以下所有记录均为虚构，用于观察表头重复、页脚以及表格最后一行。','All records below are fictional and are used to inspect repeated headers, footers, and the final table row.'),'sources':src},
       {'type':'table','headers':[pair('记录编号','Record ID'),pair('检查说明','Inspection description')],'rows':rows,'widths':[1,4],'sources':src}]}],
       'gaps':[{'field':'images','reason':'No screenshots supplied; text-only manual is intentional.','action':'omit'},{'field':'brand','reason':'No brand supplied.','action':'omit'}]}
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(d,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output_json');create(p.parse_args().output_json)
