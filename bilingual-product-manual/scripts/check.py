#!/usr/bin/env python3
"""Check complete text coverage, geometry, fields and bilingual structure."""
import argparse,json,re,sys
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from pypdf import PdfReader
from manual import load,InputError,require,PLACEHOLDER
from render import norm,NS,W,page_map

def check(input_file,out):
    data,_=load(input_file);out=Path(out);report=json.loads((out/'build-report.json').read_text());findings=[];structures={}
    for lang,info in report['languages'].items():
        with ZipFile(out/info['docx']) as z:
            root=E.fromstring(z.read('word/document.xml'));body=root.find('w:body',NS)
            texts=root.xpath('//w:t/text()',namespaces=NS)
            require(not PLACEHOLDER.search(' '.join(texts)),f'{lang}: output contains a template marker')
            geom=root.find('.//w:pgSz',NS);require(geom.get(W+'w')=='12240' and geom.get(W+'h')=='15840','Page geometry differs from the source')
            external=[]
            for n in z.namelist():
                if n.endswith('.rels'):
                    external += [x.get('Target') for x in E.fromstring(z.read(n)) if x.get('TargetMode')=='External']
            require(not external,f'{lang}: external package relationships present')
            require(not any(n.startswith(('customXml/','word/comments','word/embeddings')) for n in z.namelist()),'Unexpected private or embedded parts')
            structures[lang]={'headings':len(info['headings']),'tables':len(root.findall('.//w:tbl',NS)),'figures':len(root.findall('.//w:drawing',NS))}
        pdf=out/info['pdf'];reader=PdfReader(pdf);pdf_text=''.join(norm(p.extract_text() or '') for p in reader.pages)
        require(len(reader.pages)==info['page_count'],'PDF page count drift')
        require(len(list((out/info['png_directory']).glob('page-*.png')))==len(reader.pages),'Missing page image')
        missing=[]
        for p in body.xpath('.//w:p',namespaces=NS):
            if p.find('.//w:instrText',NS) is not None:continue
            txt=norm(''.join(p.xpath('.//w:t/text()',namespaces=NS)))
            if len(txt)>1 and txt not in pdf_text:missing.append(txt[:100])
        require(not missing,f'{lang}: PDF text missing or corrupted: {missing[:5]}')
        mapping,_=page_map(pdf,info['headings']);require(mapping==info['page_map'],'Heading page map drift')
        for p in body.findall('w:p',NS):
            instr=''.join(p.xpath('.//w:instrText/text()',namespaces=NS));m=re.search(r'PAGEREF\s+(\S+)',instr)
            if m:
                cached=p.xpath('.//w:t/text()',namespaces=NS)[-1];require(cached==str(mapping[m[1]]),'Stale DOCX TOC cache')
        findings.append({'language':lang,'pages':len(reader.pages),'text_coverage':'passed','toc_caches':'passed','geometry':'passed','placeholders':'none','package_relationships':'internal-only'})
    require(structures['zh']==structures['en'],'Bilingual structure mismatch')
    result={'automated_checks':'passed','visual_review':'required-separately','languages':findings,'structure':structures,'gap_count':len(data.get('gaps',[]))}
    (out/'qa-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output_directory');a=p.parse_args()
    try:check(a.input,a.output_directory)
    except (InputError,KeyError,ValueError) as e:print('QA ERROR: '+str(e),file=sys.stderr);sys.exit(2)
