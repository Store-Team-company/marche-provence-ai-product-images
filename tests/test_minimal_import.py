import csv
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import autopilot

class SKUImagesExportTests(unittest.TestCase):
    def test_only_two_columns_and_five_urls(self):
        catalog_path=Path('input/catalog.csv')
        row=autopilot.selection(catalog_path,1)[0]
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            folder=base/'assets'/autopilot.clean(row['SKU'])
            folder.mkdir(parents=True)
            for role in autopilot.ROLES:
                Image.new('RGB',(800,800),'white').save(folder/autopilot.filename(row,role),'WEBP')
            p=base/'import.csv'
            count=autopilot.staging_import_sku_images(catalog_path,[row],base/'assets',p,
                'https://marcheprovence.com/storage/marche-provence-images')
            self.assertEqual(count,1)
            with p.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f)
                self.assertEqual(reader.fieldnames,['SKU','Images'])
                out=list(reader)
            self.assertEqual(len(out),1)
            self.assertEqual(out[0]['SKU'],row['SKU'])
            urls=out[0]['Images'].split(',')
            self.assertEqual(len(urls),5)
            self.assertTrue(all('/marche-provence-images/' in u for u in urls))
            self.assertTrue(all('/'+row['SKU']+'/' not in u for u in urls))
    def test_incomplete_product_is_not_exported(self):
        c=Path('input/catalog.csv')
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'empty.csv'
            n=autopilot.staging_import_sku_images(c,autopilot.selection(c,1),Path(d)/'no-assets',
                dest,'https://marcheprovence.com/storage/marche-provence-images')
            self.assertEqual(n,0)
if __name__=='__main__':
    unittest.main()
