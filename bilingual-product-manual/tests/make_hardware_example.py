"""Recreate synthetic diagram fixtures and wholly fictional hardware input."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont

def pair(zh,en):return {'zh':zh,'en':en}
def create(destination):
    destination=Path(destination);images=destination/'hardware-images';images.mkdir(parents=True,exist_ok=True)
    ink='#102A4C';blue='#1465CB';pale='#EFF6FD';font=ImageFont.load_default(size=35);small=ImageFont.load_default(size=25)
    logo=Image.new('RGBA',(850,190),'white');draw=ImageDraw.Draw(logo);draw.polygon([(35,95),(87,38),(140,95),(87,152)],fill=blue);draw.text((170,48),'PAPER LAB',font=ImageFont.load_default(size=78),fill=ink);logo.save(images/'fictional-logo.png')
    for role in ['hero','detail']:
        im=Image.new('RGBA',(1280,720),(255,255,255,0));d=ImageDraw.Draw(im)
        if role=='hero':
            d.polygon([(130,220),(900,150),(1140,280),(370,360)],fill='#D1DEEA',outline=ink,width=5)
            d.polygon([(130,220),(370,360),(370,570),(130,420)],fill='#51708D',outline=ink,width=5)
            d.polygon([(370,360),(1140,280),(1140,490),(370,570)],fill='#294A69',outline=ink,width=5)
            d.text((400,225),'PSH-06',font=ImageFont.load_default(size=64),fill=ink)
            d.text((480,306),'FICTIONAL DEVICE',font=small,fill=ink)
            d.rectangle((450,417,535,483),fill='#0D223A',outline='#D6E3F0',width=3)
            for x in [610,760]:d.rounded_rectangle((x,423,x+95,458),radius=16,fill='#0D223A',outline='#D6E3F0',width=3)
            d.text((452,491),'LAN',font=small,fill='white');d.text((625,466),'USB-C',font=small,fill='white');d.text((773,466),'USB-C',font=small,fill='white')
        else:
            d.rounded_rectangle((170,180,1110,480),radius=24,fill='#D6E3F0',outline=ink,width=5)
            d.text((210,205),'PSH-06 / FICTIONAL',font=font,fill=ink)
            d.rectangle((260,310,410,405),fill=ink);d.text((280,420),'RJ45 x 1',font=small,fill=ink)
            for x in [520,790]:d.rounded_rectangle((x,325,x+160,375),radius=23,fill=ink);d.text((x+30,420),'USB-C',font=small,fill=ink)
            d.line((170,550,1110,550),fill=blue,width=3);d.line((170,530,170,570),fill=blue,width=3);d.line((1110,530,1110,570),fill=blue,width=3)
            d.text((460,570),'164 x 92 x 34 mm',font=font,fill=blue)
        d.text((300,660),'SYNTHETIC TEST DIAGRAM - NOT A REAL PRODUCT',font=small,fill=ink);im.save(images/(role+'.png'))
    source=['fictional-brief']
    def fact(value,unit=''):return {'value':value,'unit':unit,'sources':source}
    def row(id,zh,en,zv,ev):return {'id':id,'label':pair(zh,en),'value':pair(zv,ev),'sources':source}
    def feature(id,zh,en,zt,et):return {'id':id,'title':pair(zh,en),'text':pair(zt,et),'sources':source}
    data={'schema_version':1,'templates':['hardware-brochure','hardware-specification'],'fictional':True,
      'meta':{'product':pair('纸舟数据采集盒','Paperboat Signal Hub'),'model':'PSH-06','version':'0.6.0','subtitle':pair('培训用信号记录与导出','Signal recording for training'),'overview':pair('纸舟数据采集盒是一款虚构的培训设备，用于演示信号记录、状态查看和文件导出。该示例的产品、参数、图像及测试条件均为虚构。','Paperboat Signal Hub is a fictional training device for demonstrating signal recording, status review, and file export. The product, specifications, diagrams, and test conditions in this example are all fictional.'),'ordering':pair('PSH-06：示例配置为 {{fact:channels}} 个记录通道、{{fact:storage}} 存储；没有选配项。','PSH-06: the example configuration has {{fact:channels}} recording channels and {{fact:storage}} storage; no options are specified.'),'sources':source},
      'sources':[{'id':'fictional-brief','description':'Completely fictional hardware brief and synthetic diagrams created only to test this template. No real capability or certification is asserted.','fictional':True}],
      'facts':{'channels':fact('6'),'storage':fact('32','GB'),'interval':fact('30','s'),'power_v':fact('5','V'),'power_a':fact('2','A'),'power_w':fact('7','W'),'ethernet':fact('1'),'usb':fact('2'),'width':fact('164','mm'),'depth':fact('92','mm'),'height':fact('34','mm'),'weight':fact('0.48','kg'),'temp_low':fact('0','°C'),'temp_high':fact('45','°C'),'retention':fact('4096'),'delay':fact('1.5','s')},
      'brand':{'name':pair('纸舟虚构实验室','Paperboat Fictional Lab'),'logo':'hardware-images/fictional-logo.png','website':'hardware.example.invalid','email':'docs@hardware.example.invalid','sources':source},
      'images':{role:{'path':'hardware-images/'+role+'.png','model':'PSH-06','interface_check':'matched','review_notes':pair('虚构图显示 {{fact:ethernet}} 个 RJ45 和 {{fact:usb}} 个 USB-C，与本次资料一致。','The fictional diagram shows {{fact:ethernet}} RJ45 and {{fact:usb}} USB-C ports, matching this input.'),'caption':pair('虚构产品示意图，仅供模板测试。','Fictional product diagram for template testing only.'),'sources':source} for role in ['hero','detail']},
      'metrics':[{'id':'channels','label':pair('示例记录通道数','Example recording channels'),'fact':'channels','unit_label':pair('通道','channels')},{'id':'storage','label':pair('示例内置存储','Example internal storage'),'fact':'storage'},{'id':'interval','label':pair('示例记录间隔','Example recording interval'),'fact':'interval'}],
      'spec_groups':[{'id':'technical','title':pair('技术参数','Technical specifications'),'rows':[
        row('channels','记录通道','Recording channels','{{fact:channels}} 个通道','{{fact:channels}} channels'),row('storage','内置存储','Internal storage','{{fact:storage}}；无选配项','{{fact:storage}}; no options specified'),row('interval','记录间隔','Recording interval','每 {{fact:interval}} 记录','Records every {{fact:interval}}'),row('ethernet','网络接口','Network interface','{{fact:ethernet}} 个 RJ45','{{fact:ethernet}} RJ45 port'),row('usb','USB 接口','USB interfaces','{{fact:usb}} 个 USB-C','{{fact:usb}} USB-C ports'),row('retention','记录容量','Record capacity','最多 {{fact:retention}} 条示例记录','At most {{fact:retention}} example records'),
        row('power','电源输入','Power input','{{fact:power_v}} DC / {{fact:power_a}}','{{fact:power_v}} DC / {{fact:power_a}}'),row('consumption','示例功耗','Example consumption','{{fact:power_w}}','{{fact:power_w}}'),row('temperature','使用温度','Operating temperature','{{fact:temp_low}} 至 {{fact:temp_high}}','{{fact:temp_low}} to {{fact:temp_high}}'),row('dimensions','尺寸','Dimensions','{{fact:width}} × {{fact:depth}} × {{fact:height}}','{{fact:width}} × {{fact:depth}} × {{fact:height}}'),row('weight','重量','Weight','{{fact:weight}}','{{fact:weight}}')]}],
      'features':[feature('record','记录演示','Recording demo','按固定间隔保存示例信号。','Saves example signals at a fixed interval.'),feature('review','状态查看','Status review','查看最近记录及剩余容量。','Shows recent records and remaining capacity.'),feature('export','文件导出','File export','导出当前选定的记录。','Exports the currently selected records.'),feature('local','本地操作','Local operation','在培训环境中离线操作。','Runs offline in a training environment.')],
      'applications':[feature('classroom','课堂培训','Classroom training','演示数据记录的基本流程。','Demonstrates the basic recording workflow.'),feature('workshop','设备工作坊','Device workshop','讲解接口与存储的关系。','Explains interfaces and storage.'),feature('demo','产品演示','Product demonstration','展示虚构设备的操作流程。','Shows the fictional device workflow.'),feature('layout','版式测试','Layout testing','验证双语资料的布局。','Checks bilingual document layouts.')],
      'performance':{'title':pair('示例验证指标','Example validation metrics'),'intro':pair('本页仅演示指标表样式，数值不代表真实硬件测试结果。','This page demonstrates the metrics table layout. The values do not represent actual hardware test results.'),'headers':[pair('项目','Item'),pair('示例指标','Example metric')],'rows':[{'cells':[pair('状态显示延迟','Status display delay'),pair('≤ {{fact:delay}}','≤ {{fact:delay}}')],'sources':source},{'cells':[pair('记录间隔','Recording interval'),pair('{{fact:interval}}','{{fact:interval}}')],'sources':source}],'conditions':pair('虚构条件：培训演示环境；本页全部数值仅供模板测试，不构成产品承诺。','Fictional conditions: a training demonstration environment. All values on this page are template test data and make no product commitment.'),'sources':source},
      'brochure':{'hero':{'eyebrow':pair('虚构硬件示例','FICTIONAL HARDWARE'),'title':pair('记录信号\n理解数据','Record signals\nUnderstand data'),'text':pair('为培训演示组织信号、记录与导出流程。','Organize signals, records, and export workflows for training.'),'sources':source},'design':{'title':pair('桌面式设计\n便于教学展示','Desktop format\nfor demonstrations'),'text':pair('图示接口与本次虚构参数逐项对应。采用 {{fact:power_v}} DC 供电。','The illustrated ports match the fictional specification. Powered by {{fact:power_v}} DC.'),'sources':source},'parameter_columns':[['channels','storage','interval','ethernet','usb','retention'],['power','consumption','temperature','dimensions','weight']],'feature_ids':['record','review','export','local'],'application_ids':['classroom','workshop','demo','layout'],'closing':{'title':pair('虚构资料说明','Fictional example'),'text':pair('所有产品事实与图像均为模板测试数据。','All product facts and diagrams are synthetic template test data.'),'sources':source}},
      'gaps':[{'field':'certifications','reason':'No certification evidence was supplied; no certification is claimed.','action':'omit'}]}
    (destination/'fictional-hardware.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');return data

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination');create(p.parse_args().destination)
