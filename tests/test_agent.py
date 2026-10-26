import csv
import tempfile
import unittest
from pathlib import Path
import agent
class CatalogTests(unittest.TestCase):
 def test_slug(self):
  self.assertEqual(agent.slug('TT152 Red & Yellow'), 'tt152-red-yellow')
 def test_image_roles(self):
  row={'SKU':'TT152','Name':'Red Poppies Yellow'}
  files=agent.expected(row)
  self.assertEqual(len(files),5)
  self.assertTrue(all(f.endswith('.webp') for f in files))
 def test_headers(self):
  self.assertEqual(len(agent.FIELDS),15)
if __name__=='__main__': unittest.main()
