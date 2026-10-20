#!/usr/bin/env python3
"""Render paired manuals, materialize TOC caches, and export page images."""
from __future__ import annotations
import argparse,json,os,shutil,subprocess,sys,tempfile,re
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from xml.sax.saxutils import escape
from lxml import etree as E
from pypdf import PdfReader
from manual import InputError, require

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'

def executable(explicit, name):
    if explicit:
        p=Path(explicit).expanduser().resolve();require(p.is_file(),f'Executable not found: {p}');return str(p)
    py=Path(sys.executable)
    if py.parent.parent.name=='python' and py.parent.parent.parent.name=='dependencies':
        p=py.parent.parent.parent/'bin'/'override'/name
        require(p.is_file(),f'Codex bundled {name} missing; specify an approved renderer explicitly')
        return str(p)
    v=shutil.which(name);require(v is not None,f'{name} missing; install the official application or pass --{name}');return v

def run(cmd,env):
    p=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=180)
    if p.returncode:raise RuntimeError(f'{Path(cmd[0]).name} exited {p.returncode}: {p.stderr[-1800:]}')
    return p.stdout

def font_config(fonts,dirs,temp):
    dirs=[Path(x).expanduser().resolve() for x in dirs]
    explicit_dirs=bool(dirs)
    if shutil.which('fc-match'):
        for family in dict.fromkeys(fonts.values()):
            p=subprocess.run(['fc-match','-f','%{family}\n%{file}',family],capture_output=True,text=True,check=True)
            lines=p.stdout.splitlines()
            if not explicit_dirs:require(lines and family.casefold() in lines[0].casefold(),f'Font {family} is unavailable. Install it or configure theme.fonts with installed fonts; font substitution changes pagination.')
            if len(lines)>1 and Path(lines[1]).is_file():dirs.append(Path(lines[1]).parent)
    require(dirs,'Cannot discover fonts. Provide --font-dir for installed Latin and CJK fonts; no fonts are bundled.')
    for p in dirs:require(p.is_dir(),f'Font directory does not exist: {p}')
    conf=temp/'fonts.conf';cache=temp/'font-cache';cache.mkdir()
    conf.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig>'+''.join('<dir>'+escape(str(p))+'</dir>' for p in dict.fromkeys(dirs))+'<cachedir>'+escape(str(cache))+'</cachedir></fontconfig>',encoding='utf-8')
    return conf

def norm(s):return re.sub(r'\s+','',s).replace('\u00ad','')

def page_map(pdf, headings):
    r=PdfReader(pdf);destinations={}
    def walk(items):
        for x in items:
            if isinstance(x,list):walk(x)
            else:
                try:destinations[norm(x.title)]=r.get_destination_page_number(x)+1
                except (AttributeError,ValueError,TypeError):pass
    walk(r.outline)
    texts=[norm(p.extract_text() or '') for p in r.pages]
    result={}
    for h in headings:
        n=norm(h['title']);page=destinations.get(n)
        if page is None:
            hits=[i+1 for i,t in enumerate(texts) if n in t]
            # Contents precede body; choose the last occurrence. Numbered full
            # heading names are unique, and never part of running headers.
            require(hits,f'Heading missing from PDF, possibly missing font: {h["title"]}')
            page=hits[-1]
        result[h['bookmark']]=page
    return result,len(r.pages)

def cache_fields(path,mapping,pages):
    with ZipFile(path) as z:parts={n:z.read(n) for n in z.namelist()}
    for name in list(parts):
        if not (name=='word/document.xml' or re.fullmatch(r'word/footer\d+\.xml',name)):continue
        root=E.fromstring(parts[name])
        for p in root.xpath('//w:p',namespaces=NS):
            state=None;instruction='';texts=[]
            for run in p.findall('w:r',NS):
                fld=run.find('w:fldChar',NS)
                if fld is not None:
                    kind=fld.get(W+'fldCharType')
                    if kind=='begin':state='code';instruction='';texts=[]
                    elif kind=='separate':state='cache'
                    elif kind=='end':
                        value=None
                        m=re.search(r'PAGEREF\s+(\S+)',instruction)
                        if m and m[1] in mapping:value=str(mapping[m[1]])
                        elif 'NUMPAGES' in instruction:value=str(pages)
                        if value is not None and texts:
                            texts[0].text=value
                            for el in texts[1:]:el.text=''
                        state=None
                if state=='code':instruction+=''.join(run.xpath('w:instrText/text()',namespaces=NS))
                if state=='cache':texts+=run.findall('w:t',NS)
        parts[name]=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
    temporary=path.with_suffix('.tmp.docx')
    with ZipFile(temporary,'w',ZIP_DEFLATED) as z:
        for n,b in parts.items():z.writestr(n,b)
    temporary.replace(path)

def render(out,soffice,pdftoppm,dirs,dpi):
    out=Path(out).resolve();report=json.loads((out/'build-report.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='manual-render-') as td:
        temp=Path(td);env=os.environ.copy();env['FONTCONFIG_FILE']=str(font_config(report['fonts'],dirs,temp))
        env['TMPDIR']=str(temp);env['TEMP']=str(temp);env['TMP']=str(temp)
        for lang,info in report['languages'].items():
            source=out/info['docx'];prev=None;stable=False
            for iteration in range(4):
                dest=temp/f'{lang}-{iteration}';dest.mkdir();profile=temp/f'profile-{lang}-{iteration}'
                run([soffice,'-env:UserInstallation='+profile.as_uri(),'--headless','--norestore','--convert-to','pdf','--outdir',str(dest),str(source)],env)
                pdf=dest/(source.stem+'.pdf');require(pdf.is_file(),'Renderer produced no PDF')
                mapping,pages=page_map(pdf,info['headings']);current=(mapping,pages)
                cache_fields(source,mapping,pages)
                if current==prev:
                    shutil.copy2(pdf,out/pdf.name);stable=True;break
                prev=current
            require(stable,'Pagination did not stabilize after four renders; inspect layout before delivery')
            image_dir=out/f'pages-{lang}';image_dir.mkdir(exist_ok=True)
            for p in image_dir.glob('page-*.png'):p.unlink()
            run([pdftoppm,'-png','-r',str(dpi),str(out/pdf.name),str(image_dir/'page')],env)
            info.update({'pdf':pdf.name,'page_count':pages,'page_map':mapping,'png_directory':image_dir.name,'render_iterations':iteration+1})
            print(f'{lang}: {pages} pages, stable TOC, PNGs exported')
    report['status']='rendered-requires-visual-review'
    (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output_directory');p.add_argument('--soffice',default=os.getenv('SOFFICE_BIN'));p.add_argument('--pdftoppm',default=os.getenv('PDFTOPPM_BIN'));p.add_argument('--font-dir',action='append',default=[]);p.add_argument('--dpi',type=int,default=120);a=p.parse_args()
    try:render(a.output_directory,executable(a.soffice,'soffice'),executable(a.pdftoppm,'pdftoppm'),a.font_dir,a.dpi)
    except (InputError,RuntimeError,subprocess.SubprocessError) as e:print('RENDER ERROR: '+str(e),file=sys.stderr);return 2
    return 0
if __name__=='__main__':sys.exit(main())
