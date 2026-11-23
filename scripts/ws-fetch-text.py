#!/usr/bin/env python3
"""Fetch the proofread page texts of one work from a Wikisource.

usage: ws-fetch-text.py SITE "File name.djvu" FIRST LAST OUTDIR
       ws-fetch-text.py SITE @FILES.txt FIRST LAST OUTDIR
OUTDIR: data/<wikisource>/<work>/provenance/wikisource
@FILES.txt: for works with one image file per page: the file names, one per
line; page n is line n.
SITE: de.wikisource.org, la.wikisource.org, ...
Writes OUTDIR/<n>.json for every page of proofread level 3 or 4: title,
level, revision id and time stamp, contributors and the wikitext. One
request per page, with a pause (wsapi.py). Pages which are there are kept.
"""
import json, os, sys
from wsapi import api
site, name, first, last, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
PAGE_NS = {'de': 'Seite', 'la': 'Pagina', 'en': 'Page', 'fr': 'Page', 'el': 'Σελίδα'}[site.split('.')[0]]
os.makedirs(out, exist_ok=True)
files = [l.rstrip('\n') for l in open(name[1:], encoding='utf-8') if l.strip()] if name.startswith('@') else None
for n in range(first, last + 1):
    f = f'{out}/{n}.json'
    if os.path.exists(f): continue
    if files and n > len(files): break
    title = f'{PAGE_NS}:{files[n - 1]}' if files else f'{PAGE_NS}:{name}/{n}'
    d = api(site, action='query', titles=title, prop='proofread|revisions|contributors', rvprop='ids|timestamp|content',
            rvslots='main', pclimit='500')
    p = d['query']['pages'][0]
    q = p.get('proofread', {}).get('quality')
    if p.get('missing') or q is None:
        print(n, 'missing'); continue
    r = p['revisions'][0]
    json.dump({'site': site, 'title': p['title'], 'page': n, 'level': q, 'revid': r['revid'], 'timestamp': r['timestamp'],
               'contributors': [c['name'] for c in p.get('contributors', [])], 'anonymous': p.get('anoncontributors', 0),
               'wikitext': r['slots']['main']['content']}, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(n, 'level', q, 'revision', r['revid'], flush=True)
