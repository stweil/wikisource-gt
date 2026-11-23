#!/usr/bin/env python3
"""Survey of a Wikisource dump (pages-articles.xml.bz2) for early prints
whose page texts keep the forms of the print.

usage: ws-survey.py DUMP.xml.bz2 OUT.tsv
Reads the page namespace (proofread pages) and the index namespace. Writes
one row per index (scan file): year (from the index page, else from the
title), pages by proofread level (0-4), characters, pages with long s, with
small e above, with abbreviation signs, share of text lines which end in a
hyphen (line breaks of the print kept), mean line length, title."""
import bz2, collections, re, sys
import xml.etree.ElementTree as ET
dump, out = sys.argv[1:3]
ABBR = re.compile('[ꝛꝰꝑꝓꝗꝙꝯ⁊ꝫ̃̄᷑ᷣ]')
PAGE_NS = {'Seite', 'Pagina', 'Page'}; INDEX_NS = {'Index', 'Liber'}
ns_page = ns_index = None
idx = collections.defaultdict(lambda: collections.Counter()); year = {}
def clean(t):
    t = re.sub(r'<noinclude>.*?</noinclude>', '', t, flags=re.S)
    t = re.sub(r'<ref[^>]*>.*?</ref>|<[^>]+>', '', t, flags=re.S)
    t = re.sub(r'\{\{[^{}]*\}\}', '', t)
    return t
n = 0
for ev, el in ET.iterparse(bz2.open(dump, 'rb'), events=('end',)):
    tag = el.tag.rsplit('}', 1)[-1]
    if tag == 'namespace':
        if el.text in PAGE_NS: ns_page = el.get('key')
        if el.text in INDEX_NS: ns_index = el.get('key')
    if tag != 'page': continue
    g = lambda name: next((c for c in el.iter() if c.tag.rsplit('}', 1)[-1] == name), None)
    ns = g('ns').text; title = g('title').text; tx = g('text'); text = (tx.text or '') if tx is not None else ''
    if ns == ns_index:
        k = title.split(':', 1)[1]
        m = re.search(r'\|\s*(?:JAHR|Annus|Year|year|Jahr)\s*=\s*\[*(\d{4})', text)
        if m: year[k] = int(m.group(1))
    elif ns == ns_page:
        k = title.split(':', 1)[1].rsplit('/', 1)[0]
        m = re.search(r'<pagequality level="(\d)"', text); lv = m.group(1) if m else '?'
        t = clean(text); c = idx[k]; c['pages'] += 1; c['lv' + lv] += 1; c['chars'] += len(t)
        if 'ſ' in t: c['longs'] += 1
        if 'ͤ' in t: c['eabove'] += 1
        if ABBR.search(t): c['abbr'] += 1
        ls = [l.strip() for l in t.split('\n') if len(l.strip()) > 3]
        c['lines'] += len(ls); c['linechars'] += sum(map(len, ls)); c['hyph'] += sum(l[-1] in '-=⸗¬' for l in ls)
    el.clear(); n += 1
    if n % 200000 == 0: print(n, 'pages read', len(idx), 'indexes', file=sys.stderr, flush=True)
with open(out, 'w', encoding='utf-8') as f:
    f.write('year\tpages\tlv0\tlv1\tlv2\tlv3\tlv4\tchars\tlongs\teabove\tabbr\thyph%\tlinelen\ttitle\n')
    for k, c in sorted(idx.items(), key=lambda x: (year.get(x[0]) or 9999, x[0])):
        y = year.get(k)
        if not y:
            m = re.search(r'(?<!\d)(1[4-9]\d\d)(?!\d)', k); y = int(m.group(1)) if m else 0
        f.write('\t'.join(map(str, [y, c['pages'], c['lv0'], c['lv1'], c['lv2'], c['lv3'], c['lv4'], c['chars'], c['longs'], c['eabove'], c['abbr'],
                                    f"{100 * c['hyph'] / max(1, c['lines']):.1f}", f"{c['linechars'] / max(1, c['lines']):.0f}", k])) + '\n')
print('indexes', len(idx), 'with year from index page', sum(k in year for k in idx))
