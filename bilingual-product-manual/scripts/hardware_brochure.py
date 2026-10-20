"""A4 two-page blue/white brochure, with explicit overflow errors and equal tables."""
import html,math
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from hardware_common import text,selected,LABELS,require,asset_path


def paragraph(s,width,size,leading,lang,bold=False,color='102A4C'):
    style=ParagraphStyle('hardware',fontName='HardwareBold' if bold else 'HardwareRegular',fontSize=size,leading=leading,textColor=HexColor('#'+color),wordWrap='CJK' if lang=='zh' else None,spaceBefore=0,spaceAfter=0,splitLongWords=True)
    p=Paragraph(html.escape(s).replace('\n','<br/>'),style);p.wrap(width,10000);return p

def height(s,width,size,leading,lang,bold=False):return paragraph(s,width,size,leading,lang,bold).height

def table_plan(data,t):
    width=(t['brochure']['page_width_pt']-72-14)/2;mapping={r['id']:r for g in data['spec_groups'] for r in g['rows']}
    plans=[]
    for col in data['brochure']['parameter_columns']:
        rows=[]
        for id in col:
            row=mapping[id]
            label=max(height(text(data,row['label'],lang),width-20,7.5,10,lang) for lang in ('zh','en'))
            value=max(height(text(data,row['value'],lang),width-20,9.8,12.3,lang) for lang in ('zh','en'))
            rows.append({'id':id,'height':max(32,label+value+11),'label_height':label,'row':row})
        plans.append(rows)
    total=max(244,max(sum(r['height'] for r in rows) for rows in plans))
    require(total<=260,'Brochure parameter columns exceed two-page capacity; explicitly select fewer/shorter brochure rows. All specifications remain in the specification document.')
    for rows in plans:
        spare=(total-sum(r['height'] for r in rows))/len(rows)
        for row in rows:row['height']+=spare
    return plans,total


class Page:
    def __init__(self,path,data,t,lang,base,logo):
        self.data=data;self.t=t;self.lang=lang;self.base=base;self.logo=logo;self.w=t['brochure']['page_width_pt'];self.h=t['brochure']['page_height_pt'];self.width=self.w-72;self.c=canvas.Canvas(str(path),pagesize=(self.w,self.h),pageCompression=1,invariant=1)
        self.c.setTitle(text(data,data['meta']['product'],lang)+' - '+LABELS[lang]['brochure']);self.c.setAuthor('');self.c.setSubject('Fictional template demonstration' if data.get('fictional') else 'Product brochure');self.expected=[];self.layout=[];self.page=0

    def txt(self,s,x,y,w,h,size=9.8,leading=13,bold=False,color='ink',record=True,align=0):
        if not s:return 0
        p=paragraph(s,w,size,leading,self.lang,bold,self.t['colors'][color]);p.style.alignment=align;require(p.height<=h+0.01,f'Brochure text overflows page {self.page}: {s[:70]}; supply a shorter brochure title/summary, preserving full detail in the specification')
        require(x>=35.9 and x+w<=self.w-35.9 and y>=0 and y+p.height<=self.h-1,'Brochure geometry outside page')
        p.drawOn(self.c,x,self.h-y-p.height)
        if record:self.expected.append(s)
        self.layout.append({'page':self.page,'type':'text','bounds':[x,y,x+w,y+p.height]})
        return p.height

    def rect(self,x,y,w,h,fill='pale',border=None,radius=0):
        c=self.c;c.setFillColor(HexColor('#'+self.t['colors'][fill]));c.setStrokeColor(HexColor('#'+self.t['colors'][border or fill]));c.setLineWidth(.65)
        if radius:c.roundRect(x,self.h-y-h,w,h,radius,fill=1,stroke=bool(border))
        else:c.rect(x,self.h-y-h,w,h,fill=1,stroke=bool(border))

    def image(self,path,x,y,w,h,role):
        im=Image.open(path);scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale
        px,py=x+(w-iw)/2,y+(h-ih)/2
        self.c.drawImage(ImageReader(im),px,self.h-py-ih,width=iw,height=ih,mask='auto')
        self.layout.append({'page':self.page,'type':'image','role':role,'bounds':[px,py,px+iw,py+ih]})

    def frame(self,n):
        self.page=n;c=self.c;ink=self.t['colors'];c.setFillColor(HexColor('#'+ink['accent']));c.rect(0,self.h-7,self.w,7,fill=1,stroke=0)
        if self.logo:
            im=Image.open(self.logo);w=self.t['logo_visible_width_mm']*72/25.4;h=w*im.height/im.width
            require(h<=29,'Logo is too tall at the shared visual width; supply a horizontal brand lockup or reduce theme.logo_visible_width_mm')
            self.image(self.logo,36,36,w,h,'logo')
        elif self.data.get('brand',{}).get('name'):
            self.txt(text(self.data,self.data['brand']['name'],self.lang),36,36,310,25,12,15,True)
        self.txt(LABELS[self.lang]['brochure'],self.w-205,44,169,13,8.5,11,color='muted',align=2)
        model=self.data['meta']['model']+' | '+LABELS[self.lang]['version']+' '+self.data['meta']['version']
        if self.data.get('fictional'):model+=' | '+LABELS[self.lang]['fiction']
        self.txt(model,36,66,self.width,13,8.5,11,color='muted')
        c.setStrokeColor(HexColor('#'+ink['line']));c.setLineWidth(.55);c.line(36,self.h-83,self.w-36,self.h-83);c.line(36,self.h-790,self.w-36,self.h-790)
        brand=self.data.get('brand',{})
        if brand.get('name'):self.txt(text(self.data,brand['name'],self.lang),36,796,self.width-20,13,8.3,11,True)
        if brand.get('address'):self.txt(text(self.data,brand['address'],self.lang),36,810,self.width-20,11,7.5,10,color='muted')
        contacts=' | '.join(brand[k] for k in ['website','email','phone'] if brand.get(k))
        if contacts:self.txt(contacts,36,823,self.width-20,11,7.5,10,color='muted')
        self.txt(str(n),self.w-49,823,13,12,7.5,10,color='muted')

    def cards(self,items,top,mode):
        if not items:return top
        width=(self.width-14)/2;rows=math.ceil(len(items)/2);heights=[]
        for row in range(rows):
            minimum=68 if mode=='applications' else 69
            for item in items[row*2:row*2+2]:
                # Share row heights across both languages for aligned bilingual cards.
                need=max(height(text(self.data,item['title'],l),width-36,11,14,l,True)+height(text(self.data,item['text'],l),width-36,9.3,12.5,l)+25 for l in ('zh','en'))
                minimum=max(minimum,need)
            heights.append(minimum)
        require(top+sum(heights)+(rows-1)*12<=765,'Brochure cards overflow; explicitly shorten the brochure selection or move detail to the specification')
        y=top
        for row,rh in enumerate(heights):
            for col,item in enumerate(items[row*2:row*2+2]):
                x=36+col*(width+14)
                self.rect(x,y,width,rh,'pale' if mode=='features' else 'paper','line' if mode=='applications' else None,7)
                if mode=='applications':self.rect(x+11,y+12,3,rh-24,'accent',radius=1)
                pad=25 if mode=='applications' else 12
                th=self.txt(text(self.data,item['title'],self.lang),x+pad,y+10,width-pad-12,rh-18,11,14,True,'ink' if mode=='applications' else 'accent')
                self.txt(text(self.data,item['text'],self.lang),x+pad,y+15+th,width-pad-12,rh-th-22,9.3,12.5,color='muted' if mode=='applications' else 'ink')
            y+=rh+12
        return y-12


def build_brochure(data,base,out,t,logo):
    t=__import__('copy').deepcopy(t);t['colors']['paper']='FFFFFF';plans,total=table_plan(data,t);report={}
    for lang in ('zh','en'):
        path=Path(out)/f'brochure-{lang}.pdf';p=Page(path,data,t,lang,base,logo);d=data['brochure'];W=p.width
        p.frame(1);title=text(data,data['meta'].get('short_title',data['meta']['product']),lang)
        y=104+p.txt(title,36,104,W,77,29,36,True)+5
        if data['meta'].get('subtitle'):y+=p.txt(text(data,data['meta']['subtitle'],lang),36,y,W,22,12.5,17,color='muted')+5
        p.txt(data['meta']['model'],36,y,W,200-y,12.5,17,True,'accent')
        p.rect(36,211,W,193,'pale',radius=11)
        hero=d['hero'];has_image='hero' in data.get('images',{});tw=183 if has_image else W-36
        y=237
        if hero.get('eyebrow'):y+=p.txt(text(data,hero['eyebrow'],lang),54,y,tw,24,8.5,12,True,'accent')+11
        y+=p.txt(text(data,hero['title'],lang),54,y,tw,64,20,26,True)+16
        p.txt(text(data,hero['text'],lang),54,y,tw,392-y,9.6,13.2,color='muted')
        if has_image:p.image(asset_path(base,data['images']['hero']['path']),244,221,W-220,174,'hero')
        metrics=data.get('metrics',[]);y=421
        if metrics:
            cw=(W-10*(len(metrics)-1))/len(metrics)
            for i,m in enumerate(metrics):
                x=36+i*(cw+10);p.rect(x,y,cw,75,'pale',radius=8);p.rect(x,y+15,3,43,'accent',radius=1)
                fact=data['facts'][m['fact']];value=fact['value'];unit=fact.get('unit','')
                if m.get('unit_label'):unit+=(' ' if unit else '')+text(data,m['unit_label'],lang)
                vw=pdfmetrics.stringWidth(value,'HardwareBold',30)
                uw=pdfmetrics.stringWidth(unit,'HardwareRegular',9.5)
                require(vw+(8+uw if unit else 0)<=cw-28,'Metric is too long for a highlight card; select a concise metric')
                p.c.setFillColor(HexColor('#'+t['colors']['accent']));p.c.setFont('HardwareBold',30);p.c.drawString(x+15,p.h-y-39,value)
                if unit:p.c.setFont('HardwareRegular',9.5);p.c.drawString(x+23+vw,p.h-y-39,unit)
                p.expected.append(value+(' '+unit if unit else ''))
                p.txt(text(data,m['label'],lang),x+15,y+48,cw-23,25,9.2,12,color='muted')
            y+=99
        apps=selected(data,'applications')
        if apps:
            y+=p.txt(LABELS[lang]['applications'],36,y,W,29,18,25,True)+9;y=p.cards(apps,y,'applications')+22
        if d.get('closing'):
            c=d['closing'];y+=p.txt(text(data,c['title'],lang),36,y,W,22,10.5,14,True,'accent')+6;p.txt(text(data,c['text'],lang),36,y,W,782-y,9.2,13,color='muted')
        p.c.showPage();p.frame(2)
        p.txt(LABELS[lang]['hardware_system'],36,104,W,39,25,33,True);p.txt(data['meta']['model'],36,141,W,20,11.5,16,True,'accent')
        has_detail='detail' in data.get('images',{});dw=260 if has_detail else W
        dh=p.txt(text(data,d['design']['title'],lang),36,183,dw,52,16,21,True)
        p.txt(text(data,d['design']['text'],lang),36,195+dh,dw,288-(195+dh),10,13.5,color='muted')
        if has_detail:p.image(asset_path(base,data['images']['detail']['path']),309,166,W-273,124,'detail')
        p.txt(LABELS[lang]['parameters'],36,294,W,23,14.5,20,True)
        cw=(W-14)/2
        for col,rows in enumerate(plans):
            x=36+col*(cw+14);y=320
            for index,r in enumerate(rows):
                p.rect(x,y,cw,r['height'],'pale' if index%2==0 else 'paper');p.txt(text(data,r['row']['label'],lang),x+10,y+5,cw-20,r['label_height'],7.5,10,color='muted')
                p.txt(text(data,r['row']['value'],lang),x+10,y+8+r['label_height'],cw-20,r['height']-10-r['label_height'],9.8,12.3)
                y+=r['height']
            p.c.setStrokeColor(HexColor('#'+t['colors']['line']));p.c.rect(x,p.h-y,cw,total,fill=0,stroke=1)
            p.layout.append({'page':2,'type':'parameter_table','column':col,'top':320,'bottom':y,'height':total,'row_ids':[r['id'] for r in rows],'row_heights':[r['height'] for r in rows]})
        y=320+total+16;features=selected(data,'features')
        if features:
            y+=p.txt(LABELS[lang]['key_features'],36,y,W,24,14.5,20,True)+9;p.cards(features,y,'features')
        p.c.save();report[lang]={'pdf':path.name,'page_count':2,'expected_text':p.expected,'layout':p.layout,'logo_visible_width_pt':t['logo_visible_width_mm']*72/25.4 if logo else None}
    return report
