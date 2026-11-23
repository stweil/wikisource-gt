#!/usr/bin/env python3
"""Choose pages of works for a selection: N proofread pages per work, evenly
spread through the book, from a Wikisource dump (no requests to the API).

usage: ws-select-pages.py DUMP.xml.bz2 WORKS.txt N OUT.tsv
WORKS.txt: one scan file name per line (as in the survey table). A page
counts if its proofread level is 3 or 4 and its text has at least MINCHARS
characters (default 1200: no plates, title pages or short pages).
OUT.tsv: file name, proofread pages, suitable pages, chosen page numbers."""
import bz2, collections, os, re, sys
import xml.etree.ElementTree as ET
dump, works, n, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
MIN = int(os.environ.get('MINCHARS', '1200'))
want = {l.rstrip('\n') for l in open(works, encoding='utf-8') if l.strip()}
ns_page = None; pages = collections.defaultdict(list); proof = collections.Counter()
for ev, el in ET.iterparse(bz2.open(dump, 'rb'), events=('end',)):
    tag = el.tag.rsplit('}', 1)[-1]
    if tag == 'namespace' and el.text in ('Seite', 'Pagina', 'Page'): ns_page = el.get('key')
    if tag != 'page': continue
    g = lambda name: next((c for c in el.iter() if c.tag.rsplit('}', 1)[-1] == name), None)
    if g('ns').text == ns_page:
        title = g('title').text.split(':', 1)[1]
        if '/' in title:
            name, num = title.rsplit('/', 1)
            if name in want and num.isdigit():
                text = g('text').text or ''; m = re.search(r'<pagequality level="(\d)"', text)
                if m and m.group(1) in '34':
                    proof[name] += 1
                    body = re.sub(r'<noinclude>.*?</noinclude>|<ref[^>]*>.*?</ref>|\{\{[^{}]*\}\}|<[^>]+>', '', text, flags=re.S)
                    if len(body) >= MIN and '{|' not in text and '<math' not in text: pages[name].append(int(num))
    el.clear()
with open(out, 'w', encoding='utf-8') as f:
    for name in sorted(want):
        p = sorted(pages[name])
        chosen = p if len(p) <= n else [p[round(k * (len(p) - 1) / (n - 1))] for k in range(n)]
        f.write(f'{name}\t{proof[name]}\t{len(p)}\t{",".join(map(str, sorted(set(chosen))))}\n')
        print(name, proof[name], len(p), len(set(chosen)))
