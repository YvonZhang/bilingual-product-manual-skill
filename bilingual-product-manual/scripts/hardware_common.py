"""Evidence-backed input and shared layout data for two hardware document types."""
from pathlib import Path
from copy import deepcopy
from io import BytesIO
import json,re
from PIL import Image, ImageChops
from manual import require,keys,pair,expand,asset_path,InputError,PLACEHOLDER

ROOT=Path(__file__).resolve().parents[1]
LANGS=('zh','en')
LABELS={
 'zh':{'brochure':'产品彩页','specification':'产品规格书','hardware':'硬件与结构','hardware_system':'硬件与系统能力','parameters':'技术参数','overview':'产品概述','ordering':'订货型号','applications':'应用场景','features':'功能与应用','key_features':'功能特性','contact':'联系方式','parameter':'参数','value':'规格','area':'领域','example':'场景示例','fiction':'虚构产品 · 模板测试','company':'公司','website':'网站','email':'邮箱','phone':'电话','address':'地址'},
 'en':{'brochure':'PRODUCT BROCHURE','specification':'PRODUCT SPECIFICATION','hardware':'Hardware and dimensions','hardware_system':'Hardware & system capabilities','parameters':'Technical specifications','overview':'Product Overview','ordering':'Ordering Model','applications':'Application scenarios','features':'Features and applications','key_features':'Key Features','contact':'Contact Information','parameter':'Parameter','value':'Specification','area':'Area','example':'Example applications','fiction':'FICTIONAL PRODUCT - TEMPLATE TEST','company':'Company','website':'Website','email':'Email','phone':'Phone','address':'Address'}}
LABELS['zh']['version']='资料版本'
LABELS['en']['version']='Revision'

def theme(data):
    t=json.loads((ROOT/'assets/hardware-theme.json').read_text())
    c=data.get('theme',{});t['colors'].update(c.get('colors',{}));t['font_family']=c.get('font_family',t['font_family']);t['logo_visible_width_mm']=c.get('logo_visible_width_mm',t['logo_visible_width_mm'])
    return t

def validate(data,base):
    keys(data,['schema_version','templates','fictional','meta','sources','facts','brand','images','metrics','spec_groups','features','applications','performance','brochure','gaps','theme'],['schema_version','templates','meta','sources','spec_groups'],'hardware input')
    require(data['schema_version']==1,'hardware schema_version must be 1')
    types=data['templates'];require(isinstance(types,list) and types and len(types)==len(set(types)) and set(types)<={'hardware-brochure','hardware-specification'},'Select hardware-brochure and/or hardware-specification')
    require(type(data.get('fictional',False)) is bool,'fictional must be boolean')
    src=data['sources'];require(isinstance(src,list) and src,'At least one evidence source is required');ids=set()
    for s in src:
        keys(s,['id','description','fictional'],['id','description'],'source')
        require(isinstance(s['id'],str) and s['id'] not in ids and s['id'],'Source IDs must be unique');ids.add(s['id'])
        require(isinstance(s['description'],str) and s['description'].strip(),'Source description required')
        require(not s.get('fictional') or data.get('fictional'),'Fictional evidence requires visible fictional labels')
    def refs(o,where):
        r=o.get('sources');require(isinstance(r,list) and r and all(x in ids for x in r),where+': evidence source IDs required')
    facts=data.get('facts',{});require(isinstance(facts,dict),'facts must be an object')
    for id,f in facts.items():
        require(re.fullmatch('[a-z][a-z0-9_-]*',id),'Invalid fact ID');keys(f,['value','unit','sources'],['value','sources'],'fact')
        require(isinstance(f['value'],str) and f['value'].strip() and isinstance(f.get('unit',''),str),'Fact value/unit must be strings')
        require(not PLACEHOLDER.search(f['value']+f.get('unit','')),'Unresolved fact marker');refs(f,'fact '+id)
    def bilingual(v,where):
        pair(v,where,facts)
        tokens=lambda s:sorted(re.findall(r'\{\{fact:([a-z][a-z0-9_-]*)\}\}',s))
        require(tokens(v['zh'])==tokens(v['en']),where+': bilingual shared-fact references differ')
        units=lambda s:sorted(re.findall(r'\d\s*(kg|mg|g|℃|°C|K|TOPS|GFLOPS|px|MP|kB|KB|MB|GB|TB|mAh|Ah|Wh|kWh|mm|cm|km|m|ms|µs|μs|ns|s|Hz|kHz|MHz|GHz|mA|A|mV|V|kW|W|%)(?![A-Za-z])',expand(s,facts)))
        require(units(v['zh'])==units(v['en']),where+': bilingual hardware unit mismatch')
        # Preserve comparison direction and range signs as well as numeric values.
        signs=lambda s:sorted(re.findall(r'<=|>=|≤|≥|<|>|±',expand(s,facts)))
        require(signs(v['zh'])==signs(v['en']),where+': bilingual comparison mismatch')
    meta=data['meta'];keys(meta,['product','short_title','model','version','subtitle','overview','ordering','sources'],['product','model','version','overview','sources'],'meta');refs(meta,'meta')
    for k in ['product','short_title','subtitle','overview','ordering']:
        if k in meta:bilingual(meta[k],'meta.'+k)
    for k in ['model','version']:
        require(isinstance(meta[k],str) and meta[k].strip() and len(meta[k])<=48,'meta.'+k+' must be a short shared string');expand(meta[k],facts)
    for k in ['features','applications']:
        values=data.get(k,[]);require(isinstance(values,list),k+' must be a list');seen=set()
        for row in values:
            keys(row,['id','title','text','sources'],['id','title','text','sources'],k)
            require(isinstance(row['id'],str) and row['id'] not in seen,k+' IDs must be unique');seen.add(row['id'])
            bilingual(row['title'],k+'.title');bilingual(row['text'],k+'.text');refs(row,k)
    metrics=data.get('metrics',[]);require(isinstance(metrics,list) and len(metrics)<=3,'At most three explicit highlight metrics');seen=set()
    for m in metrics:
        keys(m,['id','label','fact','unit_label'],['id','label','fact'],'metric');require(m['id'] not in seen,'Duplicate metric ID');seen.add(m['id'])
        require(m['fact'] in facts,'Metric must reference a shared fact');bilingual(m['label'],'metric.label')
        if 'unit_label' in m:bilingual(m['unit_label'],'metric.unit_label')
    groups=data['spec_groups'];require(isinstance(groups,list) and groups,'Provide at least one specification group');all_rows={};group_ids=set()
    for g in groups:
        keys(g,['id','title','rows'],['id','title','rows'],'spec group');require(g['id'] not in group_ids,'Duplicate specification group ID');group_ids.add(g['id']);bilingual(g['title'],'group.title')
        require(isinstance(g['rows'],list) and g['rows'],'Specification group is empty')
        for row in g['rows']:
            keys(row,['id','label','value','sources'],['id','label','value','sources'],'specification row')
            require(row['id'] not in all_rows,'Duplicate specification row ID');all_rows[row['id']]=row
            bilingual(row['label'],'row.label');bilingual(row['value'],'row.value');refs(row,'row '+row['id'])
            require(max(len(v) for v in row['value'].values())<=1800,'Split an oversized specification record into several records')
    brand=data.get('brand',{});keys(brand,['name','logo','website','email','phone','address','sources'],[],'brand')
    if brand:refs(brand,'brand')
    for k in ['name','address']:
        if k in brand:bilingual(brand[k],'brand.'+k)
    for k in ['website','email','phone']:
        if k in brand:require(isinstance(brand[k],str) and len(brand[k])<=160 and not PLACEHOLDER.search(brand[k]),'Invalid brand.'+k)
    if brand.get('logo'):asset_path(base,brand['logo'])
    images=data.get('images',{});keys(images,['hero','detail'],[],'images')
    for role,img in images.items():
        keys(img,['path','caption','model','interface_check','review_notes','sources'],['path','model','interface_check','review_notes','sources'],'image '+role)
        asset_path(base,img['path']);refs(img,'image '+role);bilingual(img['review_notes'],'image review_notes')
        if 'caption' in img:bilingual(img['caption'],'image caption')
        require(img['model']==meta['model'],'Image model does not match the current product')
        require(img['interface_check'] in ['matched','not_applicable'],'Image/interface mismatch or unverified image: resolve with the source owner before generation')
    if 'performance' in data:
        p=data['performance'];keys(p,['title','intro','headers','rows','conditions','sources'],['title','intro','headers','rows','conditions','sources'],'performance');refs(p,'performance')
        for k in ['title','intro','conditions']:bilingual(p[k],'performance.'+k)
        require(isinstance(p['headers'],list) and 2<=len(p['headers'])<=4,'Performance table needs 2..4 columns')
        for h in p['headers']:bilingual(h,'performance header')
        require(isinstance(p['rows'],list) and p['rows'],'Performance table is empty')
        for row in p['rows']:
            keys(row,['cells','sources'],['cells','sources'],'performance row');refs(row,'performance row')
            require(len(row['cells'])==len(p['headers']),'Performance row/column mismatch')
            for cell in row['cells']:bilingual(cell,'performance cell')
    if 'hardware-brochure' in types:
        b=data.get('brochure');keys(b,['hero','design','parameter_columns','feature_ids','application_ids','closing'],['hero','design','parameter_columns','feature_ids','application_ids'],'brochure')
        for role in ['hero','design']:
            keys(b[role],['eyebrow','title','text','sources'],['title','text','sources'],'brochure '+role);refs(b[role],role)
            for k in ['eyebrow','title','text']:
                if k in b[role]:bilingual(b[role][k],role+'.'+k)
        cols=b['parameter_columns'];require(isinstance(cols,list) and len(cols)==2 and all(isinstance(c,list) and c for c in cols),'Brochure needs two nonempty, explicitly selected parameter columns')
        flat=[x for c in cols for x in c];require(len(flat)==len(set(flat)) and all(x in all_rows for x in flat),'Brochure parameter IDs must exist and cannot repeat')
        for key,items in [('feature_ids',data.get('features',[])),('application_ids',data.get('applications',[]))]:
            chosen=b[key];require(isinstance(chosen,list) and len(chosen)<=4 and len(chosen)==len(set(chosen)) and all(x in {i['id'] for i in items} for x in chosen),'Brochure '+key+' must select at most four existing records')
        if 'closing' in b:
            keys(b['closing'],['title','text','sources'],['title','text','sources'],'closing');refs(b['closing'],'closing')
            bilingual(b['closing']['title'],'closing title');bilingual(b['closing']['text'],'closing text')
    require(isinstance(data.get('gaps',[]),list),'gaps must be a list')
    for g in data.get('gaps',[]):
        keys(g,['field','reason','action'],['field','reason','action'],'gap');require(g['action'] in ['omit','internal'],'Gap action must be omit or internal')
        require(all(isinstance(g[k],str) and g[k].strip() for k in g),'Gap fields must be nonempty strings')
    config=data.get('theme',{});keys(config,['font_family','colors','logo_visible_width_mm'],[],'theme')
    if 'font_family' in config:require(isinstance(config['font_family'],str) and config['font_family'].strip(),'Invalid font family')
    for k,v in config.get('colors',{}).items():require(k in ['ink','accent','muted','pale','line'] and re.fullmatch('[0-9a-fA-F]{6}',v),'Invalid theme color')
    require(12<=config.get('logo_visible_width_mm',28)<=40,'Logo width must be 12..40 mm')
    return facts

def load(path):
    path=Path(path).resolve();data=json.loads(path.read_text());validate(data,path.parent);return data,path.parent

def text(data,value,lang):
    return expand(value[lang] if isinstance(value,dict) else value,data.get('facts',{}))

def selected(data,kind):
    ids=data['brochure'][{'features':'feature_ids','applications':'application_ids'}[kind]]
    mapping={r['id']:r for r in data.get(kind,[])};return [mapping[id] for id in ids]

def normalized_logo(data,base,temp):
    value=data.get('brand',{}).get('logo')
    if not value:return None
    im=Image.open(asset_path(base,value)).convert('RGBA')
    alpha=im.getchannel('A')
    if alpha.getextrema()[0]<255:bounds=alpha.getbbox()
    else:
        rgb=im.convert('RGB');difference=ImageChops.difference(rgb,Image.new('RGB',rgb.size,'white'))
        bounds=difference.getbbox()
    require(bounds,'Logo contains no visible pixels')
    path=Path(temp)/'normalized-logo.png';im.crop(bounds).save(path)
    return path

def all_font_text(data):
    return json.dumps(data,ensure_ascii=False)+json.dumps(LABELS,ensure_ascii=False)+''.join(expand(m.group(),data.get('facts',{})) for m in re.finditer(r'\{\{fact:[a-z][a-z0-9_-]*\}\}',json.dumps(data)))+'0123456789 / | · - × % ± :'
