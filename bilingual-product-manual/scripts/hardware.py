#!/usr/bin/env python3
"""Build and render independent bilingual hardware brochures and specifications."""
import argparse,json,os,sys,tempfile,shutil,subprocess
from pathlib import Path
from pypdf import PdfReader
from hardware_common import load,theme,normalized_logo,all_font_text,require,InputError

def build(input_path,out,font_regular=None,font_bold=None):
    from hardware_fonts import register_pdf_fonts
    from hardware_brochure import build_brochure
    from hardware_spec import build_specification
    data,base=load(input_path);t=theme(data);out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    require(not (out/'hardware-build-report.json').exists() and not any(out.glob('brochure-*.pdf')) and not any(out.glob('specification-*.docx')),'Use a fresh hardware output directory')
    report={'schema_version':1,'skill_version':'2.0.0','templates':data['templates'],'fictional':data.get('fictional',False),'font_family':t['font_family'],'facts':data.get('facts',{}),'gaps':data.get('gaps',[]),'documents':{},'status':'built-render-and-visual-review-required'}
    with tempfile.TemporaryDirectory(prefix='hardware-build-') as td:
        staging=Path(td)/'artifacts';staging.mkdir()
        register_pdf_fonts(t['font_family'],all_font_text(data),td,font_regular,font_bold)
        logo=normalized_logo(data,base,td)
        if 'hardware-brochure' in data['templates']:report['documents']['hardware-brochure']=build_brochure(data,base,staging,t,logo)
        if 'hardware-specification' in data['templates']:report['documents']['hardware-specification']=build_specification(data,base,staging,t,logo)
        for artifact in staging.iterdir():shutil.copy2(artifact,out/artifact.name)
    (out/'hardware-build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'built','templates':data['templates'],'internal_gaps':len(report['gaps']),'next':'render, check, then inspect every page'},ensure_ascii=False))

def render(out,soffice,pdftoppm,dirs,dpi):
    from render import font_config,run
    out=Path(out).resolve();p=out/'hardware-build-report.json';report=json.loads(p.read_text())
    with tempfile.TemporaryDirectory(prefix='hardware-render-') as td:
        tmp=Path(td);env=os.environ.copy();env['FONTCONFIG_FILE']=str(font_config({'hardware':report['font_family']},dirs,tmp));env['TMPDIR']=str(tmp);env['TEMP']=str(tmp);env['TMP']=str(tmp)
        for kind,languages in report['documents'].items():
            for lang,doc in languages.items():
                if 'docx' in doc:
                    source=out/doc['docx'];dest=tmp/lang;dest.mkdir();profile=tmp/f'profile-{lang}'
                    run([soffice,'-env:UserInstallation='+profile.as_uri(),'--headless','--norestore','--convert-to','pdf','--outdir',str(dest),str(source)],env)
                    pdf=dest/(source.stem+'.pdf');require(pdf.is_file(),'Specification PDF was not produced');shutil.copy2(pdf,out/pdf.name);doc['pdf']=pdf.name
                pdf=out/doc['pdf'];pages=len(PdfReader(pdf).pages);directory=out/('pages-'+pdf.stem);directory.mkdir(exist_ok=True)
                for previous in directory.glob('page-*.png'):previous.unlink()
                run([pdftoppm,'-png','-r',str(dpi),str(pdf),str(directory/'page')],env)
                doc['page_count']=pages;doc['png_directory']=directory.name;print(kind,lang,pages,'pages')
    report['status']='rendered-requires-visual-review';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('validate');a.add_argument('input')
    a=sub.add_parser('build');a.add_argument('input');a.add_argument('--out',required=True);a.add_argument('--font-regular');a.add_argument('--font-bold')
    a=sub.add_parser('render');a.add_argument('output');a.add_argument('--soffice');a.add_argument('--pdftoppm');a.add_argument('--font-dir',action='append',default=[]);a.add_argument('--dpi',type=int,default=120)
    args=p.parse_args()
    try:
        if args.command=='validate':load(args.input);print('Hardware input validation passed')
        elif args.command=='build':build(args.input,args.out,args.font_regular,args.font_bold)
        else:
            from render import executable
            render(args.output,executable(args.soffice,'soffice'),executable(args.pdftoppm,'pdftoppm'),args.font_dir,args.dpi)
    except (InputError,KeyError,TypeError,OSError,json.JSONDecodeError,RuntimeError,subprocess.SubprocessError) as e:print('HARDWARE ERROR: '+str(e),file=sys.stderr);return 2
    return 0
if __name__=='__main__':sys.exit(main())
