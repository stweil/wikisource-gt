#!/usr/bin/env python3
"""Download the scan file of a work from Wikimedia Commons (one API request
and one download) and write WORKDIR/provenance/source.txt: URL, SHA-1, work name,
and the licence data of the file page into WORKDIR/provenance/scan.json.

usage: ws-get-scan.py SITE "File name.djvu" WORKDIR
       ws-get-scan.py SITE @FILES.txt WORKDIR
@FILES.txt: for works with one image file per page (page n is line n): each
image is downloaded to WORKDIR/GT-PAGE/<work>_<nnnn>.<ext>, and source.txt
gets one line per page (URL, SHA-1, image name). Two requests per page.
"""
import hashlib, json, os, re, subprocess, sys
from wsapi import api, UA
site, name, work = sys.argv[1:4]
if name.startswith('@'):
    files = [l.rstrip('\n') for l in open(name[1:], encoding='utf-8') if l.strip()]
    wn = os.path.basename(work.rstrip('/')); os.makedirs(work + '/provenance', exist_ok=True); os.makedirs(work + '/GT-PAGE', exist_ok=True)
    src = work + '/provenance/source.txt'
    have = {l.split()[2]: l for l in open(src)} if os.path.exists(src) else {}
    info = []
    for n, fn in enumerate(files, 1):
        img = f'{wn}_{n:04d}.{fn.rsplit(".", 1)[1].lower()}'
        if img in have and os.path.exists(f'{work}/GT-PAGE/{img}'): continue
        d = api(site, action='query', titles='File:' + fn, prop='imageinfo', iiprop='url|size|sha1|extmetadata')
        ii = d['query']['pages'][0]['imageinfo'][0]; url = ii['url'].split('?')[0]
        subprocess.run(['curl', '-sS', '-L', '-A', UA, '-o', f'{work}/GT-PAGE/{img}', url], check=True)
        import time; time.sleep(4)
        sha = hashlib.sha1(open(f'{work}/GT-PAGE/{img}', 'rb').read()).hexdigest()
        assert sha == ii['sha1'], 'SHA-1 differs: ' + fn
        have[img] = f'{url} {sha} {img}\n'
        open(src, 'w').write(''.join(have[k] for k in sorted(have)))
        em = ii.get('extmetadata', {}); lic = re.sub(r'<[^>]+>', '', em.get('LicenseShortName', {}).get('value', ''))
        print(n, img, ii.get('width'), 'x', ii.get('height'), lic, flush=True)
    sys.exit()
d = api(site, action='query', titles='File:' + name, prop='imageinfo', iiprop='url|size|sha1|mime|extmetadata')
ii = d['query']['pages'][0]['imageinfo'][0]
url = ii['url'].split('?')[0]; f = f'{work}/{os.path.basename(url)}'
os.makedirs(work + '/provenance', exist_ok=True)
if not os.path.exists(f) or hashlib.sha1(open(f, 'rb').read()).hexdigest() != ii['sha1']:
    subprocess.run(['curl', '-sS', '-L', '-A', UA, '-o', f, url], check=True)
sha = hashlib.sha1(open(f, 'rb').read()).hexdigest()
assert sha == ii['sha1'], 'SHA-1 differs'
em = ii.get('extmetadata', {}); txt = lambda k: re.sub(r'<[^>]+>', '', em.get(k, {}).get('value', '')).strip()
json.dump({'file': 'File:' + name, 'page': ii.get('descriptionurl'), 'url': url, 'sha1': sha, 'size': ii.get('size'), 'pages': ii.get('pagecount'),
           'width': ii.get('width'), 'height': ii.get('height'), 'licence': txt('LicenseShortName'), 'artist': txt('Artist'), 'credit': txt('Credit')},
          open(f'{work}/provenance/scan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(f'{work}/provenance/source.txt', 'w').write(f'{url} {sha} {os.path.basename(work.rstrip("/"))}\n')
print(f, ii.get('size'), 'bytes,', ii.get('pagecount'), 'pages,', txt('LicenseShortName'))
