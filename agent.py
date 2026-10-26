#!/usr/bin/env python3
"""Marché Provence CSV image workflow. Python 3.10+; Pillow for conversions."""
import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image, ImageOps

FIELDS = ['ID','Name','Slug','URL','SKU','Status','Is Featured','Labels','Taxes','Image','Images','Product Attributes','Import Type','Tags','Order']
ROLES = ['main','detail','alternate','lifestyle-garden','lifestyle-dining']
def slug(value):
    return re.sub(r'[^a-z0-9]+','-',value.lower()).strip('-')[:82]
def load(path):
    with open(path, encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError('Export headers differ from verified Botble 15-column source. Do not update.')
        rows=list(reader)
    keys=[(r['ID'],r['SKU']) for r in rows]
    if len(set(keys))!=len(keys) or any(not a or not b for a,b in keys):
        raise ValueError('Missing or duplicate ID/SKU pair')
    return rows
def expected(row):
    base=slug(row['Name']) or slug(row['SKU'])
    return [f"{slug(row['SKU'])}-{base}-{role}.webp" for role in ROLES]
def plan(args):
    rows=load(args.csv)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    with open(out/'manifest.csv','w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['ID','SKU','Name','URL','source_image','source_images','status',*ROLES])
        w.writeheader()
        for r in rows:
            is_product=r['Import Type']=='product' and r['Status']=='published'
            names=expected(r)
            w.writerow(dict(ID=r['ID'],SKU=r['SKU'],Name=r['Name'],URL=r['URL'],source_image=r['Image'],source_images=r['Images'],status='pending' if is_product and r['Image'] else 'review',**dict(zip(ROLES,names))))
    print(f"Prepared {len(rows)} rows; see {out/'manifest.csv'}")
def convert(args):
    source=Path(args.input);dest=Path(args.output);dest.mkdir(parents=True,exist_ok=True)
    count=0
    for p in source.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in ('.png','.jpg','.jpeg','.tif','.tiff','.webp'):
            continue
        rel=p.relative_to(source).with_suffix('.webp')
        target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(p) as im:
            im=ImageOps.exif_transpose(im).convert('RGB')
            im.save(target,'WEBP',quality=args.quality,method=6)
        count+=1
    print('Converted',count,'images')
def export(args):
    rows=load(args.csv)
    approved=Path(args.approved)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    url_root=args.public_base_url.rstrip('/')
    if not url_root.startswith('https://'):
        raise ValueError('Require publicly reachable HTTPS media URL')
    changes=0
    result=[]
    for row in rows:
        new=dict(row)
        if row['Import Type']=='product' and row['Status']=='published':
            directory=approved/slug(row['SKU'])
            names=expected(row)
            paths=[directory/name for name in names]
            if all(p.is_file() for p in paths) and (directory/'approved.flag').is_file():
                urls=[f"{url_root}/{slug(row['SKU'])}/{name}" for name in names]
                new['Image']=urls[0];new['Images']=','.join(urls);changes+=1
        result.append(new)
    with open(out,'w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(result)
    with open(out.with_suffix('.summary.json'),'w') as f:
        json.dump({'total_rows':len(result),'updated_products':changes,'preserved_rows':len(result)-changes,
                   'note':'URLs must exist in public media storage BEFORE importing. No store changes made.'},f,indent=2)
    print(f'Exported {len(result)} original-format rows with {changes} approved image-only replacements')
def main():
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest='command',required=True)
    a=sp.add_parser('plan');a.add_argument('--csv',required=True);a.add_argument('--output',default='output')
    a=sp.add_parser('convert');a.add_argument('--input',required=True);a.add_argument('--output',required=True);a.add_argument('--quality',type=int,default=83)
    a=sp.add_parser('export');a.add_argument('--csv',required=True);a.add_argument('--approved',required=True);a.add_argument('--output',required=True);a.add_argument('--public-base-url',required=True)
    args=p.parse_args();{'plan':plan,'convert':convert,'export':export}[args.command](args)
if __name__=='__main__':main()
