#!/usr/bin/env python3
"""Create per-image alt and media title CSV; no claims beyond product name and image role."""
import argparse
import csv
import re
from pathlib import Path
from agent import load, expected

ROLE_DESCRIPTION = {
 'main': ('product photograph', 'Full product view'),
 'detail': ('fabric detail', 'Close-up of fabric and printed design'),
 'alternate': ('alternate view', 'Additional view'),
 'lifestyle-garden': ('garden table setting', 'Outdoor lifestyle setting'),
 'lifestyle-dining': ('dining table setting', 'Indoor lifestyle setting'),
}
ROLES=list(ROLE_DESCRIPTION)
def clean_title(value):
    value=re.sub(r'\$\s*\d+(?:\.\d{2})?','',value)
    value=re.sub(r'\b(?:seats?\s*\d+[–-]\d+)\b','',value,flags=re.I)
    value=re.split(r'\s+[–—]\s+',value)[0]
    value=re.sub(r'\s+',' ',value).strip(' -–—!,')
    return value[:95]
def build(row, role, filename):
    product=clean_title(row['Name'])
    type_name, setting=ROLE_DESCRIPTION[role]
    # Human-readable, describe the actual view; do not keyword-stuff.
    alt=f"{product} — {type_name}"
    title=f"{product} | {setting}"
    return {
      'ID':row['ID'],'SKU':row['SKU'],'Image Role':role,
      'Filename':filename, 'Image Alt':alt[:150],
      'Image Title':title[:150],
      'Product URL':row['URL'],
      'QA Status':'REVIEW — verify actual image matches the words'
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--csv',required=True)
    p.add_argument('--output',default='output/image-seo-metadata.csv')
    args=p.parse_args()
    rows=load(args.csv); output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    fields=['ID','SKU','Image Role','Filename','Image Alt','Image Title','Product URL','QA Status']
    with output.open('w',encoding='utf-8-sig',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader()
        for row in rows:
            if row['Import Type']!='product' or row['Status']!='published': continue
            for role,filename in zip(ROLES,expected(row)):
                writer.writerow(build(row,role,filename))
    print('Created:',output)
if __name__=='__main__': main()
