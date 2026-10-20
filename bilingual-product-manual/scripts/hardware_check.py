#!/usr/bin/env python3
"""Check full text, layouts, brands, bilingual data and native specification structure."""
import argparse,json,re,sys
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import pdfplumber
from pypdf import PdfReader
from hardware_common import load,require,InputError,PLACEHOLDER,theme,LABELS

def norm(s):return re.sub(r'\s+','',s).replace('\u00ad','').replace('•','').replace('\u200b','')

def check(input_path,out):
    data,_=load(input_path);out=Path(out);report=json.loads((out/'hardware-build-report.json').read_text());t=theme(data)
    require(report['templates']==data['templates'],'Requested template list differs from output')
    result={'automated_checks':'passed','visual_review':'required-separately','documents':{},'bilingual_facts':'validated-shared-facts-and-translations','logo_widths_pt':[],'gap_count':len(report['gaps'])}
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for kind,languages in report['documents'].items():
        result['documents'][kind]={}
        for lang,doc in languages.items():
            pdf=out/doc['pdf'];r=PdfReader(pdf);contents='\n'.join(p.extract_text() or '' for p in r.pages);normalized=norm(contents)
            for expected in doc['expected_text']:require(norm(expected) in normalized,kind+' '+lang+': missing PDF text '+expected[:80])
            require(not PLACEHOLDER.search(contents),'Unresolved placeholder in output PDF')
            require(norm(data['meta']['version']) in normalized,'Input document revision is missing from PDF')
            require(not data.get('fictional') or ('虚构产品' if lang=='zh' else 'FICTIONALPRODUCT') in normalized,'Fictional notice missing')
            for page in r.pages:require(abs(float(page.mediabox.width)-595.28)<.1 and abs(float(page.mediabox.height)-841.89)<.1,'Hardware page must be A4')
            pngs=list((out/doc['png_directory']).glob('page-*.png'));require(len(pngs)==len(r.pages),'Not all PDF pages were rendered')
            actual_logo_widths=[]
            with pdfplumber.open(pdf) as pdfdata:
                for page in pdfdata.pages:
                    doc_label=LABELS[lang]['brochure' if kind=='hardware-brochure' else 'specification']
                    headings=[hit for hit in page.search(doc_label,regex=False) if hit['top']<80]
                    require(any(abs(hit['x1']-(page.width-36))<.3 for hit in headings),'Header document label is not aligned to the right content margin')
                    for ch in page.chars:
                        if not ch['text'].strip():continue
                        require(ch['x0']>=33 and ch['x1']<=page.width-32 and ch['top']>=4 and ch['bottom']<=page.height-3,'PDF text falls outside its permitted area')
                    if data.get('brand',{}).get('logo'):
                        logos=[im for im in page.images if im['top']<80 and im['x0']<150]
                        require(len(logos)==1,'Expected one visible header logo on every page')
                        im=logos[0];actual_logo_widths.append(im['width'])
                        require(abs(im['width']-t['logo_visible_width_mm']*72/25.4)<.12,'Rendered logo width differs from shared brand configuration')
                        require(abs(im['x0']-36)<.25,'Rendered logo is not aligned to the left content margin')
            if kind=='hardware-brochure':
                require(len(r.pages)==2,'Brochure must remain exactly two pages')
                tables=[x for x in doc['layout'] if x['type']=='parameter_table'];require(len(tables)==2 and abs(tables[0]['bottom']-tables[1]['bottom'])<.01,'Brochure parameter columns have unequal bottoms')
                result['documents'][kind][lang]={'pages':len(r.pages),'text_coverage':'passed','equal_parameter_table_bottoms':True,'bottom_pt':tables[0]['bottom']}
            else:
                with ZipFile(out/doc['docx']) as z:
                    require(not any(x.startswith(('customXml/','word/embeddings/')) for x in z.namelist()),'Unwanted DOCX data or embedded object')
                    xml=E.fromstring(z.read('word/document.xml'));count=len(xml.xpath('//w:tbl',namespaces=ns))
                    require(count>0,'Specification must use native editable tables')
                    for tbl in xml.xpath('//w:tbl',namespaces=ns):
                        require(tbl.find('w:tr/w:trPr/w:tblHeader',ns) is not None,'Table header is not repeatable')
                        for row in tbl.findall('w:tr',ns):require(row.find('w:trPr/w:cantSplit',ns) is not None,'Table record may split across pages')
                        require(not tbl.xpath('.//w:trHeight[@w:hRule="exact"]',namespaces=ns),'Exact row height may clip text')
                    for name in z.namelist():
                        if name.endswith('.rels'):require(b'TargetMode="External"' not in z.read(name),'External relationship in specification')
                result['documents'][kind][lang]={'pages':len(r.pages),'text_coverage':'passed','native_tables':count,'repeating_headers':'passed','whole_records':'passed'}
                from hardware_common import text
                page_text=[norm(page.extract_text() or '') for page in r.pages]
                for g in data['spec_groups']:
                    for row in g['rows']:
                        cells=[norm(text(data,row[k],lang)) for k in ['label','value']]
                        require(any(all(cell in page for cell in cells) for page in page_text),'Specification record is divided between pages: '+row['id'])
            result['logo_widths_pt'].extend(actual_logo_widths)
    widths=result['logo_widths_pt'];require(not widths or max(widths)-min(widths)<.12,'Logo visual width differs across documents')
    if 'hardware-brochure' in result['documents']:
        b=result['documents']['hardware-brochure'];require(abs(b['zh']['bottom_pt']-b['en']['bottom_pt'])<.01,'Bilingual brochure tables differ in total height')
    (out/'hardware-qa-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2));return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output');a=p.parse_args()
    try:check(a.input,a.output)
    except (InputError,KeyError,OSError) as e:print('HARDWARE QA ERROR: '+str(e),file=sys.stderr);return 2
    return 0
if __name__=='__main__':sys.exit(main())
