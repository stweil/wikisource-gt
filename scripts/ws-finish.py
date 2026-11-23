#!/usr/bin/env python3
"""Write work.yml and CONTRIBUTORS.md of a work from the fetched data.

usage: ws-finish.py WORKDIR "Title" YEAR [key=value ...]
Reads provenance/wikisource/*.json, provenance/scan.json (if there) and
provenance/build.json; extra key=value pairs go into work.yml."""
import collections, glob, json, os, sys, urllib.parse
work, title, year = sys.argv[1:4]; extra = dict(a.split('=', 1) for a in sys.argv[4:])
pages = [json.load(open(f, encoding='utf-8')) for f in glob.glob(work + '/provenance/wikisource/*.json')]
site = pages[0]['site']; c = collections.Counter(); anon = 0
for d in pages: c.update(d['contributors']); anon += d.get('anonymous', 0)
b = json.load(open(work + '/provenance/build.json', encoding='utf-8'))
scan = json.load(open(work + '/provenance/scan.json', encoding='utf-8')) if os.path.exists(work + '/provenance/scan.json') else {}
t0 = pages[0]['title']; index = t0.split(':', 1)[1].rsplit('/', 1)[0] if '/' in t0 else ''
y = {'title': title, 'year': year, 'wikisource': site}
if index: y['index'] = f'https://{site}/wiki/Index:' + urllib.parse.quote(index.replace(' ', '_'))
if scan: y.update({'scan': scan.get('page'), 'scan-licence': scan.get('licence'), 'scan-size': f"{scan.get('width')} x {scan.get('height')} pixels, {scan.get('pages')} pages"})
y.update({'text-licence': 'CC BY-SA 4.0', 'text-fetched': max(d['timestamp'] for d in pages)[:0] or extra.pop('fetched', ''), 'last-revision': max(d['timestamp'] for d in pages),
          'proofread-pages': sum(d['level'] >= 3 for d in pages), 'transcription-level': 'level2', 'models': ', '.join(b['models']),
          'tailed-z': 'ʒ (U+0292)' if b['zform'] == 'ʒ' else 'z', 'pages': b.get('PAGE files', 0), 'lines-used': b.get('lines used', 0), 'lines-left-out': b.get('lines left out', 0)})
if b.get('eszett'): y['eszett'] = f"the print sets {b['eszett']} for ß"
y.update(extra)
open(work + '/work.yml', 'w', encoding='utf-8').write(''.join(f'{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, str) and (":" in v or v == "") else v}\n' for k, v in y.items()))
open(work + '/CONTRIBUTORS.md', 'w', encoding='utf-8').write(f'# Contributors of the Wikisource text\n\nWork: {title} ({site})\n\nUsers who edited the pages used here (number of pages), from the page\nhistories as fetched:\n\n'
    + '\n'.join(f'- {n} ({k})' for n, k in c.most_common()) + (f'\n- anonymous edits on {anon} pages' if anon else '') + '\n')
print(work, y['pages'], 'pages,', y['lines-used'], 'lines used,', len(c), 'contributors')
