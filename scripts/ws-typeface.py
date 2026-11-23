#!/usr/bin/env python3
"""Classify works of a Wikisource by typeface from one page in the middle.

usage: ws-typeface.py SITE SURVEY.tsv MINYEAR MINPAGES MODEL TESSDATA OUTDIR
SURVEY.tsv: table of ws-survey.py. For every work (scan file with pages
<name>/<n>) of MINYEAR or later with at least MINPAGES pages: fetch a page
image of 1280 px from the middle of the file (two requests, wsapi.py),
recognise it and count long s. A print with long s is Fraktur (or an old
Antiqua); one without is modern Antiqua. Writes OUTDIR/typeface.tsv (year,
pages, proofread, class, share of long s, letters, mean confidence is not
used, file) and keeps the images in OUTDIR/img/.
"""
import hashlib, os, re, subprocess, sys
from wsapi import api, get
site, survey, miny, minp, model, tessdata, out = sys.argv[1:8]
T = os.path.expanduser(os.environ.get('TESSERACT', 'tesseract'))
os.makedirs(out + '/img', exist_ok=True)
done = {l.rstrip('\n').split('\t')[-1] for l in open(out + '/typeface.tsv', encoding='utf-8')} if os.path.exists(out + '/typeface.tsv') else set()
rows = [l.rstrip('\n').split('\t') for l in open(survey, encoding='utf-8')][1:]
rows = [r for r in rows if int(r[0]) >= int(miny) and int(r[1]) >= int(minp) and re.search(r'\.(djvu|pdf)$', r[13], re.I)]
with open(out + '/typeface.tsv', 'a', encoding='utf-8') as f:
    for k, r in enumerate(sorted(rows, key=lambda r: -int(r[1]))):
        name = r[13]
        if name in done: continue
        try:
            d = api(site, action='query', titles='File:' + name, prop='imageinfo', iiprop='size')
            ii = d['query']['pages'][0].get('imageinfo', [{}])[0]; n = max(1, (ii.get('pagecount') or int(r[1])) // 2)
            d = api(site, action='query', titles='File:' + name, prop='imageinfo', iiprop='url', iiurlparam=f'page{n}-1280px')
            url = d['query']['pages'][0]['imageinfo'][0]['thumburl']
            jpg = f'{out}/img/{hashlib.sha1(name.encode()).hexdigest()[:12]}.jpg'; open(jpg, 'wb').write(get(url, binary=True))
            t = subprocess.run([T, jpg, '-', '--tessdata-dir', tessdata, '-l', model, '--psm', '3'], capture_output=True, text=True,
                               env=dict(os.environ, OMP_THREAD_LIMIT='1')).stdout
            letters = sum(c.isalpha() for c in t); ls = t.count('ſ')
            share = ls / max(1, letters)
            cls = 'few letters' if letters < 300 else 'Fraktur' if share > 0.01 else 'Antiqua' if share < 0.002 else 'unclear'
        except Exception as e:
            cls, share, letters, n = 'error: ' + str(e)[:60], 0, 0, 0
        f.write('\t'.join(map(str, [r[0], r[1], int(r[5]) + int(r[6]), cls, f'{100 * share:.2f}', letters, n, name])) + '\n'); f.flush()
        print(r[0], cls, f'{100 * share:.2f}', name, flush=True)
