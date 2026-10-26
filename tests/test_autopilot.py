import unittest
import tempfile
from io import BytesIO
from pathlib import Path
from PIL import Image
import autopilot

class AutopilotTests(unittest.TestCase):
    def test_catalog_and_first_100(self):
        path=Path('input/catalog.csv')
        self.assertEqual(len(autopilot.catalog(path)),408)
        self.assertEqual(len(autopilot.selection(path,100)),100)
    def test_safe_reference_allowlist(self):
        r={'Image':'https://bad.com/storage/x.jpg',
           'Images':'http://marcheprovence.com/storage/a.jpg,https://marcheprovence.com/storage/b.jpg'}
        self.assertEqual(autopilot.urls(r),['https://marcheprovence.com/storage/b.jpg'])
    def test_deterministic_filenames(self):
        r={'Name':'$34 Poppies on Yellow Round Tablecloth','SKU':'TT152'}
        self.assertTrue(autopilot.filename(r,'main').startswith('tt152-'))
        self.assertTrue(autopilot.filename(r,'main').endswith('-main.webp'))
    def test_webp_800(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp=BytesIO()
            Image.new('RGB',(400,650),'white').save(inp,'PNG')
            path=Path(tmp)/'out.webp'
            autopilot.webp_800(inp.getvalue(),path)
            self.assertTrue(autopilot.valid(path))
    def test_image_only_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            original='input/catalog.csv'
            first=autopilot.selection(original,1)[0]
            for role in autopilot.ROLES:
                path=root/'assets'/autopilot.clean(first['SKU'])/autopilot.filename(first,role)
                path.parent.mkdir(parents=True,exist_ok=True)
                Image.new('RGB',(800,800),'white').save(path,'WEBP')
            count=autopilot.staging_import(original,[first],root/'assets',root/'import.csv','https://example.com/media')
            self.assertEqual(count,1)
            old=autopilot.catalog(original)
            new=autopilot.catalog(root/'import.csv')
            self.assertEqual(len(old),len(new))
            for a,b in zip(old,new):
                self.assertEqual({k:v for k,v in a.items() if k not in ('Image','Images')},
                                 {k:v for k,v in b.items() if k not in ('Image','Images')})

if __name__=='__main__':
    unittest.main()
