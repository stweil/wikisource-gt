#!/usr/bin/env python3
"""Second look at the works which ws-typeface.py could not classify ("few
letters", "unclear"): two more pages, at 30 % and 70 % of the scan file.

usage: ws-typeface2.py SITE OUTDIR MODEL TESSDATA
reads OUTDIR/typeface.tsv, writes OUTDIR/typeface2.tsv: year, pages,
proofread, class, share of long s per page (30 %, 70 %), letters, file."""
import hashlib, os, subprocess, sys
from wsapi import api, get
site, out, model, tessdata = sys.argv[1:5]
T = os.path.expanduser(os.environ.get('TESSERACT', 'tesseract'))
rows = [l.rstrip('\n').split('\t') for l in open(out + '/typeface.tsv', encoding='utf-8')]
with open(out + '/typeface2.tsv', 'w', encoding='utf-8') as f:
    for r in rows:
        if r[3] not in ('few letters', 'unclear'): continue
        name = r[7]; res = []
        try:
            d = api(site, action='query', titles='File:' + name, prop='imageinfo', iiprop='size')
            pc = d['query']['pages'][0]['imageinfo'][0].get('pagecount') or int(r[1])
            for share in (0.3, 0.7):
                n = max(1, int(pc * share))
                d = api(site, action='query', titles='File:' + name, prop='imageinfo', iiprop='url', iiurlparam=f'page{n}-1280px')
                jpg = f'{out}/img/{hashlib.sha1(name.encode()).hexdigest()[:12]}-{n}.jpg'
                open(jpg, 'wb').write(get(d['query']['pages'][0]['imageinfo'][0]['thumburl'], binary=True))
                t = subprocess.run([T, jpg, '-', '--tessdata-dir', tessdata, '-l', model, '--psm', '3'], capture_output=True, text=True,
                                   env=dict(os.environ, OMP_THREAD_LIMIT='1')).stdout
                res.append((sum(c.isalpha() for c in t), t.count('ſ')))
            good = [(a, b) for a, b in res if a >= 300]
            sh = [b / a for a, b in good]
            cls = ('few letters' if not good else 'Fraktur' if all(x > 0.01 for x in sh) else 'Antiqua' if all(x < 0.002 for x in sh)
                   else 'mixed' if any(x > 0.01 for x in sh) and any(x < 0.002 for x in sh) else 'unclear')
        except Exception as e:
            cls = 'error: ' + str(e)[:60]
        f.write('\t'.join(map(str, [r[0], r[1], r[2], cls, ' / '.join(f'{100 * b / max(1, a):.2f}' for a, b in res), ' / '.join(str(a) for a, _ in res), name])) + '\n'); f.flush()
        print(r[0], cls, res, name, flush=True)
