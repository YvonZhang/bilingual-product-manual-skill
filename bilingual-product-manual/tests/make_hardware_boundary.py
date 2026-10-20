"""Make a fictional long-title, 54-record, no-images/no-brand hardware case."""
import argparse,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def create(destination):
    d=json.loads((ROOT/'examples/fictional-hardware.json').read_text());d.pop('brand');d.pop('images');d.pop('performance')
    d['meta']['product']={'zh':'纸舟课堂信号采集、状态核对与离线文件导出综合培训设备','en':'Paperboat Classroom Signal Collection, Status Review and Offline File Export Training Device'}
    d['meta']['short_title']={'zh':'纸舟培训设备','en':'Paperboat Training Device'}
    d['meta']['overview']={'zh':'本虚构培训设备用于演示信号记录、状态查看和文件导出。产品与参数均为虚构，本次没有提供图片或性能测试资料。','en':'This fictional training device demonstrates signal recording, status review and file export. The product and specifications are fictional. No images or performance test evidence were supplied.'}
    d['brochure']['design']['text']={'zh':'参数按本次虚构资料整理。采用 {{fact:power_v}} DC 供电。','en':'The specifications follow this fictional input. Powered by {{fact:power_v}} DC.'}
    d['brochure']['closing']['text']={'zh':'所有产品事实均为模板测试数据。','en':'All product facts are synthetic template test data.'}
    d['meta'].pop('subtitle',None)
    rows=d['spec_groups'][0]['rows']
    for i in range(len(rows)+1,55):
        rows.append({'id':'training-record-'+str(i),'label':{'zh':f'培训记录 {i}','en':f'Training record {i}'},'value':{'zh':f'记录 {i}：此项为虚构的表格换行与跨页测试说明，不代表实际硬件性能。','en':f'Record {i}: this fictional explanatory entry checks wrapping and pagination across a long specification table. It makes no hardware performance claim.'},'sources':['fictional-brief']})
    d['gaps'] += [{'field':k,'reason':'Not supplied in this fictional boundary input','action':'omit'} for k in ['brand','images','performance']]
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True);p=destination/'hardware-boundary.json';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return p
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination');print(create(p.parse_args().destination))
