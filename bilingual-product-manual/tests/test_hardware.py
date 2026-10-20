import copy,json,sys,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from hardware_common import validate,InputError
from hardware import build

class HardwareBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'examples/fictional-hardware.json').read_text());self.base=ROOT/'examples'
    def rejects(self,fn):
        fn(self.data)
        with self.assertRaises(InputError):validate(self.data,self.base)
    def test_missing_translation_rejected(self):self.rejects(lambda d:d['meta']['product'].pop('en'))
    def test_inconsistent_numeric_capacity_rejected(self):self.rejects(lambda d:d['spec_groups'][0]['rows'][0].update(value={'zh':'6','en':'7'}))
    def test_mass_units_rejected(self):self.rejects(lambda d:d['spec_groups'][0]['rows'][-1].update(value={'zh':'0.48 kg','en':'0.48 g'}))
    def test_comparison_direction_rejected(self):self.rejects(lambda d:d['performance']['rows'][0].update(cells=[{'zh':'延迟','en':'Delay'},{'zh':'≤ 1.5 s','en':'≥ 1.5 s'}]))
    def test_equal_values_cannot_hide_different_fact_sources(self):self.rejects(lambda d:d['spec_groups'][0]['rows'][0].update(value={'zh':'{{fact:channels}}','en':'6 channels'}))
    def test_unverified_photo_rejected(self):self.rejects(lambda d:d['images']['hero'].update(interface_check='unverified'))
    def test_wrong_interface_photo_rejected(self):self.rejects(lambda d:d['images']['hero'].update(interface_check='mismatch'))
    def test_wrong_model_photo_rejected(self):self.rejects(lambda d:d['images']['hero'].update(model='OTHER-01'))
    def test_parent_asset_escape_rejected(self):self.rejects(lambda d:d['brand'].update(logo='../logo.png'))
    def test_unprovided_evidence_rejected(self):self.rejects(lambda d:d['performance'].update(sources=['missing-evidence']))
    def test_performance_without_test_conditions_rejected(self):self.rejects(lambda d:d['performance'].pop('conditions'))
    def test_no_silent_fictional_label_removal(self):self.rejects(lambda d:d.update(fictional=False))
    def test_public_draft_marker_rejected(self):self.rejects(lambda d:d['meta'].update(overview={'zh':'TBD','en':'TBD'}))
    def test_repeated_brochure_parameter_rejected(self):self.rejects(lambda d:d['brochure']['parameter_columns'][1].append('channels'))
    def test_software_schema_does_not_enter_hardware_pipeline(self):self.rejects(lambda d:d.update(templates=['software-manual']))
    def run_build(self,data,out):
        # Input uses the existing test assets only; all files stay in temporary output.
        inp=out.parent/'input.json';inp.write_text(json.dumps(data,ensure_ascii=False))
        data=copy.deepcopy(data);data.pop('images',None);data.pop('brand',None)
        inp.write_text(json.dumps(data,ensure_ascii=False));build(inp,out)
    def test_brochure_overflow_fails_instead_of_shrinking_or_omitting(self):
        d=copy.deepcopy(self.data);d['meta']['product']={'zh':'极长标题'*60,'en':'Unacceptably lengthy official product title '*60}
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(InputError,'overflows'):self.run_build(d,Path(td)/'out')
    def test_long_brochure_table_fails_instead_of_discarding_rows(self):
        d=copy.deepcopy(self.data)
        for row in d['spec_groups'][0]['rows']:row['value']={'zh':'长参数说明'*15,'en':'A long parameter explanation '*15}
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(InputError,'capacity'):self.run_build(d,Path(td)/'out')
    def test_missing_optional_data_removes_images_performance_and_brand(self):
        d=copy.deepcopy(self.data);d.pop('performance');d['templates']=['hardware-specification']
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out';self.run_build(d,out)
            report=json.loads((out/'hardware-build-report.json').read_text());self.assertEqual(len(report['gaps']),1)
            for lang in ['zh','en']:
                self.assertTrue(any('0.6.0' in s for s in report['documents']['hardware-specification'][lang]['expected_text']))
                with ZipFile(out/f'specification-{lang}.docx') as z:
                    xml=z.read('word/document.xml').decode();self.assertNotIn('<w:drawing',xml);self.assertNotIn('hardware.example.invalid',xml);self.assertNotIn('No certification evidence',xml);self.assertNotIn('{{fact:',xml)
                    self.assertIn('0.6.0',z.read('word/header1.xml').decode())
                    self.assertFalse(any(n.startswith('customXml/') for n in z.namelist()))
                    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};tree=E.fromstring(z.read('word/document.xml'))
                    self.assertFalse(tree.xpath('//w:trHeight[@w:hRule="exact"]',namespaces=ns))
                    self.assertNotIn('Example validation metrics',xml)

if __name__=='__main__':unittest.main()
