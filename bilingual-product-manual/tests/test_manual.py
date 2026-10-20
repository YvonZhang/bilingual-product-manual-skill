import json,sys,tempfile,unittest,copy,shutil,subprocess
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from manual import validate,InputError,build

class ManualBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'examples/fictional-product.json').read_text())
        self.base=ROOT/'examples'
    def rejects(self,change):
        change(self.data)
        with self.assertRaises(InputError):validate(self.data,self.base)
    def test_missing_english_cannot_silently_emit_chinese_twice(self):
        self.rejects(lambda d:d['meta']['product'].pop('en'))
    def test_different_numeric_capacity_is_rejected(self):
        self.rejects(lambda d:d['sections'][0]['blocks'][0].update(text={'zh':'最多 15 条','en':'At most 16 entries'}))
    def test_different_units_are_rejected(self):
        self.rejects(lambda d:d['sections'][0]['blocks'][0].update(text={'zh':'延时 15 ms','en':'Delay 15 s'}))
    def test_negative_sign_is_not_lost_in_translation(self):
        self.rejects(lambda d:d['sections'][0]['blocks'][0].update(text={'zh':'温度 -5 °C','en':'Temperature 5 °C'}))
    def test_unresolved_fact_is_rejected(self):
        self.rejects(lambda d:d['sections'][0]['blocks'][0].update(text={'zh':'{{fact:unknown}}','en':'{{fact:unknown}}'}))
    def test_visible_draft_markers_are_rejected(self):
        self.rejects(lambda d:d['meta'].update(intro={'zh':'TODO','en':'TODO'}))
    def test_unsupported_specification_mode_is_rejected(self):
        self.rejects(lambda d:d.update(template='hardware-specification'))
    def test_unknown_source_is_rejected(self):
        self.rejects(lambda d:d['facts']['interval'].update(sources=['unprovided-source']))
    def test_incomplete_table_record_is_rejected(self):
        self.rejects(lambda d:d['sections'][6]['blocks'][2]['rows'][0].pop())
    def test_heading_gap_is_rejected(self):
        self.rejects(lambda d:d['sections'][0].update(level=3))
    def test_missing_figure_is_rejected(self):
        self.rejects(lambda d:d['sections'][4]['blocks'][2].update(path='images/missing.png'))
    def test_tall_record_cannot_be_clipped_by_row_keep_rule(self):
        def change(d):
            table=d['sections'][6]['blocks'][2]
            table['widths']=[1,8,1]
            table['rows'][0][0]={'zh':'很长的说明文字'*100,'en':'Very long explanatory text '*40}
        self.rejects(change)
    def test_asset_parent_escape_is_rejected(self):
        self.rejects(lambda d:d['sections'][4]['blocks'][2].update(path='../outside.png'))
    def test_fictional_source_cannot_lose_visible_label(self):
        self.rejects(lambda d:d.update(fictional=False))
    def test_optional_brand_images_and_gaps_do_not_become_public_placeholders(self):
        d=copy.deepcopy(self.data);d.pop('brand')
        for s in d['sections']:s['blocks']=[b for b in s['blocks'] if b['type']!='figure']
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'product.json';p.write_text(json.dumps(d));out=Path(td)/'out';build(p,out)
            report=json.loads((out/'build-report.json').read_text());self.assertEqual(len(report['gaps']),1)
            for lang in ('zh','en'):
                with ZipFile(out/f'manual-{lang}.docx') as z:
                    x=z.read('word/document.xml').decode();self.assertNotIn('No certification information',x);self.assertNotIn('docs.example.invalid',x)
                    self.assertNotIn('<w:drawing',x);self.assertNotIn('{{fact:',x)
    def test_fresh_relocated_skill_works_outside_its_cwd(self):
        with tempfile.TemporaryDirectory(prefix='portable manual ') as td:
            new=Path(td)/'renamed skill';shutil.copytree(ROOT,new,ignore=shutil.ignore_patterns('__pycache__'))
            out=Path(td)/'new result'
            p=subprocess.run([sys.executable,str(new/'scripts/manual.py'),'build',str(new/'examples/fictional-product.json'),'--out',str(out)],cwd=td,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertTrue((out/'manual-zh.docx').is_file());self.assertTrue((out/'manual-en.docx').is_file())

if __name__=='__main__':unittest.main()
