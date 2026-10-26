#!/usr/bin/env python3
"""Resumable, reference-led OpenAI photo production. Stages assets; never deploys."""
from __future__ import annotations
import argparse
import base64
import csv
from datetime import datetime, timezone
from contextlib import ExitStack
from io import BytesIO
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlparse
import hashlib
import requests
from PIL import Image, ImageOps

ROLES = ('main','detail','alternate','lifestyle-garden','lifestyle-dining')
HEADERS = ['ID','Name','Slug','URL','SKU','Status','Is Featured','Labels','Taxes', 'Image','Images','Product Attributes','Import Type','Tags','Order']
HOSTS = {'marcheprovence.com', 'www.marcheprovence.com'}
MODEL = 'gpt-image-2.5-sunburst'

def clean(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def product_slug(row):
    # Preserve descriptive product terms and remove unnecessary dollar amounts.
    name = re.sub(r'\$\s*\d+(?:\.\d\d)?', '', row['Name'])
    # cap the slug while ensuring SKU always prevents collisions.
    return clean(name)[:68].rstrip('-')

def filename(row, role):
    return f"{clean(row['SKU'])}-{product_slug(row)}-{role}.webp"

def catalog(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != HEADERS:
            raise ValueError('Unexpected CSV headers, refusing to create import')
        rows=list(reader)
    keys=[(r['ID'], r['SKU']) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate ID / SKU keys')
    return rows

def selection(path, limit=100):
    return [r for r in catalog(path) if r['Import Type']=='product' and r['Status']=='published'][:limit]

def urls(row):
    found=[]
    for raw in [row.get('Image','')] + row.get('Images','').split(','):
        raw=raw.strip()
        url=urlparse(raw)
        if (url.scheme == 'https' and url.hostname in HOSTS and url.port is None and
                not url.username and not url.password and url.path.startswith('/storage/')
                and raw not in found):
            found.append(raw)
    return found[:3]

def load_reference(url, session=None):
    session=session or requests
    with session.get(url, timeout=(12,40), stream=True, allow_redirects=False) as res:
        res.raise_for_status()
        if 300 <= res.status_code < 400:
            raise ValueError('Redirects not allowed')
        content=BytesIO(); n=0
        for chunk in res.iter_content(65536):
            n += len(chunk)
            if n > 14*1024*1024:
                raise ValueError('Reference too large')
            content.write(chunk)
    content.seek(0)
    with Image.open(content) as im:
        if im.width < 180 or im.height < 180:
            raise ValueError('Reference image too small')
        im=ImageOps.exif_transpose(im).convert('RGB')
        im.thumbnail((1600,1600), Image.Resampling.LANCZOS)
        out=BytesIO(); im.save(out,format='PNG')
        out.name='source.png'; out.seek(0)
        return out

def prompts(row,role):
    name=row['Name'].strip()
    n=name.lower()
    if 'ensemble' in n or 'set' in n:
        kind='coordinated textile ensemble, show all pieces actually pictured as included'
    elif 'basket' in n or 'tidy' in n:
        kind='soft fabric bread basket, preserve its exact shape and ties'
    elif 'runner' in n:
        kind='table runner, do not convert to a tablecloth'
    elif 'placemat' in n:
        kind='placemat, preserve rectangular or round shape from reference'
    elif 'napkin' in n:
        kind='fabric napkin, preserve sewn edging and print'
    else:
        kind='tablecloth as pictured, preserve shape and border'
    base=(f'This is a real ecommerce item, SKU {row["SKU"]}, called {name}. {kind}. '
      'Edit the provided original image to create a realistic merchandise photograph. '
      'Maintain the precise original textile print, motif density, orientation, color scheme, hem, border, silhouette and actual contents. '
      'Do NOT invent a new textile design or new accessories; no text/branding/watermark/price. '
      'The first reference image is authoritative for the sold item, others are for clarity only. '
      'Keep the fabric recognizable and unobstructed. Square commercial photography. ')
    views={
      'main':'Clean hero/catalog photograph of the whole exact item, bright neutral background, no people, item fully visible.',
      'detail':'Detailed close-up of the true fabric weave, original design and stitching. Use only motifs present in the reference.',
      'alternate':'Another realistic full-product view from a different angle in a softly styled room, no people.',
      'lifestyle-garden':'An authentic American home garden or green lawn patio setting with this EXACT textile in use. One or two relatable middle-aged adults, attractive warm daylight, product prominently visible.',
      'lifestyle-dining':'A second genuine lifestyle situation with the same textile at a real home dining table or terrace, two adults where appropriate. Natural not fashion-model posing. Print must remain exact.'
    }
    return base+views[role]

def image_edit(client, row, role, original, extra_refs=(), retries=2):
    ref_files=[original] + list(extra_refs)
    for attempt in range(retries+1):
        try:
            with ExitStack() as stack:
                fobjs=[]
                for i, buf in enumerate(ref_files):
                    buf.seek(0)
                    # BytesIO is compatible with OpenAI's Uploadable; assign an explicit filename.
                    f=BytesIO(buf.read()); f.name=f'reference-{i}.png'
                    fobjs.append(stack.enter_context(f))
                res=client.images.edit(model=MODEL, image=fobjs, prompt=prompts(row,role),
                                       n=1,size='1024x1024',quality='medium',output_format='webp',
                                       output_compression=86)
            raw=res.data[0].b64_json
            if not raw:
                raise RuntimeError('Empty base64 payload')
            return base64.b64decode(raw,validate=True)
        except Exception as e:
            if attempt >= retries:
                raise RuntimeError(f'OpenAI generation failed after {retries+1} attempts: {e}') from e
            time.sleep(min(60,5*(2**attempt)))

def webp_800(data,out):
    with Image.open(BytesIO(data)) as im:
        im=ImageOps.exif_transpose(im).convert('RGB')
        im=ImageOps.contain(im,(800,800),Image.Resampling.LANCZOS)
        canvas=Image.new('RGB',(800,800),'white')
        canvas.paste(im,((800-im.width)//2,(800-im.height)//2))
        out.parent.mkdir(parents=True,exist_ok=True)
        canvas.save(out,format='WEBP',quality=83,method=6)
    with Image.open(out) as test:
        if test.format!='WEBP' or test.size != (800,800):
            raise ValueError('Invalid converted image')

def valid(path):
    if not path.is_file(): return False
    try:
        with Image.open(path) as im:
            return im.format=='WEBP' and im.size==(800,800) and im.mode=='RGB'
    except (OSError,ValueError):
        return False

def status(rows,assets):
    results=[]
    for row in rows:
        folder=assets/clean(row['SKU'])
        imgs=[filename(row,role) for role in ROLES]
        files=[folder/n for n in imgs]
        done=sum(valid(p) for p in files)
        results.append({'ID':row['ID'],'SKU':row['SKU'],'Name':row['Name'],
                        'Generated':done,'Required':5,'Status':'NEEDS_VISUAL_QA' if done==5 else ('PARTIAL' if done else 'PENDING'),
                        'Images':'|'.join(imgs)})
    return results

def seo_metadata(row,role):
    name=re.sub(r'\$\s*\d+(?:\.\d\d)?','',row['Name']).strip()[:100]
    title={
        'main':'Product Photo','detail':'Pattern and Fabric Detail','alternate':'Alternate Product View',
        'lifestyle-garden':'Outdoor Garden Setting','lifestyle-dining':'Dining Table Lifestyle'
    }[role]
    return f'{name} | {title}'[:155], f'{name} — {title.lower()}'[:160]

def write_reports(rows,assets,reports,base_url='https://marcheprovence.com/storage/imported-product-images'):
    reports.mkdir(parents=True,exist_ok=True)
    states=status(rows,assets)
    with (reports/'progress.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['ID','SKU','Name','Generated','Required','Status','Images'])
        w.writeheader();w.writerows(states)
    with (reports/'seo-image-metadata.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['ID','SKU','Filename','Role','Image Title','Image Alt','State']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in rows:
            for role in ROLES:
                fname=filename(row,role)
                title,alt=seo_metadata(row,role)
                file=assets/clean(row['SKU'])/fname
                w.writerow({'ID':row['ID'],'SKU':row['SKU'],'Filename':fname,'Role':role,
                    'Image Title':title,'Image Alt':alt,'State':'NEEDS_VISUAL_QA' if valid(file) else 'PENDING'})
    # Future URL fields intentionally not present in live import until batch is complete.
    summary={'updated_at_utc':datetime.now(timezone.utc).isoformat(),'target_products':len(rows),
             'complete_technical':sum(s['Generated']==5 for s in states),
             'images_generated':sum(s['Generated'] for s in states),
             'total_expected_images':len(rows)*5,
             'production_deployed':False,'auto_approved':False,
             'warning':'Technical success is not visual fidelity approval.'}
    (reports/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return summary

def staging_import(catalog_path,rows,assets,out,base_url):
    if not base_url.startswith('https://'):
        raise ValueError('Only HTTPS staging URLs allowed')
    all_rows=catalog(catalog_path)
    eligible={(r['ID'],r['SKU']) for r in rows}
    updates=0
    for row in all_rows:
        if (row['ID'],row['SKU']) not in eligible:
            continue
        folder=assets/clean(row['SKU'])
        paths=[folder/filename(row,role) for role in ROLES]
        if not all(valid(f) for f in paths):
            continue
        # URLs intentionally refer to FUTURE server upload; do not import before deployment.
        web=[f"{base_url.rstrip('/')}/{clean(row['SKU'])}/{p.name}" for p in paths]
        row['Image']=web[0];row['Images']=','.join(web)
        updates+=1
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=HEADERS);w.writeheader();w.writerows(all_rows)
    return updates

def run(args):
    rows=selection(args.catalog,args.limit)
    assets=Path(args.assets);reports=Path(args.reports)
    start=time.monotonic()
    summary=write_reports(rows,assets,reports)
    if summary['complete_technical'] == len(rows):
        print('Batch complete. No more generation.');return
    if not os.getenv('OPENAI_API_KEY'):
        print('BLOCKED: Set GitHub Actions secret OPENAI_API_KEY. No OpenAI calls made.')
        (reports/'BLOCKED.txt').write_text('Missing OPENAI_API_KEY. Add the secret under repository Settings > Secrets and variables > Actions.\n')
        return
    from openai import OpenAI
    client=OpenAI(timeout=160, max_retries=0)
    new=0
    failures=[]
    # Handle incomplete SKUs first, then new SKUs; stop at job budget.
    rows.sort(key=lambda r:(-sum(valid(assets/clean(r['SKU'])/filename(r,role)) for role in ROLES),r['ID']))
    for row in rows:
        folder=assets/clean(row['SKU'])
        pending=[role for role in ROLES if not valid(folder/filename(row,role))]
        if not pending:continue
        if new>=args.max_images or time.monotonic()-start>=args.time_budget:break
        refs=[]
        for url in urls(row):
            try:refs.append(load_reference(url))
            except Exception as exc:failures.append(f'{row["SKU"]}: source {url}: {type(exc).__name__} {exc}')
        if not refs:
            failures.append(f'{row["SKU"]}: NO_SOURCE_REFERENCES; skipped')
            continue
        for role in pending:
            if new>=args.max_images or time.monotonic()-start>=args.time_budget:break
            try:
                data=image_edit(client,row,role,refs[0],refs[1:2],retries=args.retries)
                path=folder/filename(row,role)
                webp_800(data,path)
                new+=1
                print(f'CREATED {row["SKU"]} {role}: {path}',flush=True)
            except Exception as exc:
                failures.append(f'{row["SKU"]} {role}: {exc}')
                # Stop this SKU on API issues, continue next SKU.
                break
        write_reports(rows,assets,reports)
    if failures:
        with (reports/'failures.log').open('a',encoding='utf-8') as f:
            for line in failures:f.write(datetime.now(timezone.utc).isoformat()+' '+line[:900]+'\n')
    summary=write_reports(rows,assets,reports)
    print(json.dumps({'run_generated':new,**summary},indent=2),flush=True)
    if summary['complete_technical']==len(rows):
        staging_import(args.catalog,rows,assets,reports/'images-only-import-STAGING-DO-NOT-UPLOAD.csv',args.future_url)
        (reports/'100_READY_FOR_REVIEW.txt').write_text(
            '100 product sets generated at 800x800 WebP; pending HUMAN visual print/contents QA. '\
            'Images are in private GitHub, NOT uploaded to server. STAGING CSV URL fields do not exist until server deployment.\n')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--catalog',default='input/catalog.csv')
    p.add_argument('--assets',default='assets')
    p.add_argument('--reports',default='reports')
    p.add_argument('--limit',type=int,default=100)
    p.add_argument('--max-images',type=int,default=35)
    p.add_argument('--time-budget',type=int,default=2950)
    p.add_argument('--retries',type=int,default=1)
    p.add_argument('--future-url',default='https://marcheprovence.com/storage/imported-product-images')
    p.add_argument('--report-only',action='store_true')
    args=p.parse_args()
    if not 1 <= args.limit <= 100 or not 1 <= args.max_images <= 50 or args.time_budget>3100:
        p.error('batch bounds exceeded')
    if args.report_only:
        print(json.dumps(write_reports(selection(args.catalog,args.limit),Path(args.assets),Path(args.reports)),indent=2))
    else:
        run(args)
if __name__=='__main__':main()