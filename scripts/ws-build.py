#!/usr/bin/env python3
"""Build line ground truth in PAGE XML for one Wikisource work.

usage: ws-build.py WORKDIR NAME MODEL1 MODEL2 TESSDATA [FIRST LAST]
reads  WORKDIR/provenance/wikisource/<n>.json  (ws-fetch-text.py)
       WORKDIR/<scan file>.djvu or .pdf  (from Wikimedia Commons, ws-get-scan.py)
writes WORKDIR/GT-PAGE/NAME_<nnnn>.png and .xml, WORKDIR/.ocr/ (cache),
       WORKDIR/provenance/lines.tsv

Wikisource gives the text of every printed line, proofread twice, but
normalised: round s for long s, abbreviations with a bar expanded (vnd for
vñ, truncken for trunckẽ), r for r rotunda. The line image shows the forms
of the print. So each page is recognised with two models; a recognised line
gets its stretch of the Wikisource text of the page (Wikisource moves
split words to the next line, so its line breaks are not always those of
the print), and the two are compared letter by letter. A difference is allowed only where it is a known pair of print form
and normalised form (table PAIRS). A line is used when both models lead to
the same text and every other letter agrees with Wikisource. Its text has
the letters of Wikisource and the print forms of the recognition. All other
lines are left out, kept in the PAGE file as XML comments and listed in
provenance/lines.tsv. The Wikisource text of the whole page is a comment at the end.

Following the OCR-D guidelines (level 2) the virgule is written without a
blank before it and with one after it.
"""
import collections, difflib, glob, json, os, re, subprocess, sys, unicodedata
import xml.etree.ElementTree as ET

work, name, M1, M2, TESSDATA = sys.argv[1:6]
first, last = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (1, 10 ** 6)
T = os.path.expanduser(os.environ.get('TESSERACT', 'tesseract'))
NS = 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15'
ET.register_namespace('', NS)
q = lambda t: f'{{{NS}}}{t}'

# print form (one unit of the recognition) -> normalised forms which Wikisource may have for it
VOW = 'aeiouyAEIOUY'
PAIRS = {'ſ': ['s'], 'ꝛ': ['r'], 'ð': ['der', 'de'], 'ꝰ': ['us'], 'ꝑ': ['per', 'par'], 'ꝓ': ['pro'],
         'ꝗ': ['que'], '⁊': ['vnd', 'und', 'et'], 'ꝯ': ['con', 'com'], 'ñ': ['nn', 'nd'], 'n̄': ['nn', 'nd'], 'm̃': ['mm'], 'm̄': ['mm']}
for v, w in zip('aouAOU', 'äöüÄÖÜ'): PAIRS[v + '\u0364'] = [w]      # historic umlaut, where Wikisource writes the modern one
PAIRS['⸗'] = ['-']
# i/j and u/v as printed: where both models read the other letter of the pair
# than Wikisource (jhn / ihn, vnd / und), the print form of the models is taken
NOSUBST = set(PAIRS)      # print forms: never replaced by a plain letter of Wikisource
for a_, b_ in ('ji', 'ij', 'vu', 'uv'): PAIRS.setdefault(a_, []).append(b_)
for v in VOW:
    for mark in '̃̄':
        PAIRS[unicodedata.normalize('NFC', v + mark)] = [v + 'n', v + 'm']
ZFORM = os.environ.get('ZFORM', 'ʒ')     # the tailed z of early prints is written ʒ (U+0292); ZFORM=z for prints with a plain z
SCAN = os.path.basename((glob.glob(f'{work}/*.djvu') + glob.glob(f'{work}/*.pdf') + [''])[0])   # '' : one image file per page, already in GT-PAGE
# For PDF scans: resolution of the page images. Chosen per work so that the
# embedded scan is not scaled (pdfimages -list); kept as fourth field of provenance/source.txt.
_src = open(f'{work}/provenance/source.txt').read().split() if os.path.exists(f'{work}/provenance/source.txt') else []
DPI = os.environ.get('DPI') or (_src[3] if len(_src) == 4 else '')
if not DPI and SCAN.endswith('.pdf'):
    # resolution of the embedded scans: the highest of the first pages (a PDF may
    # hold a coarse background and a fine text layer), between 72 and 400
    ppi = [float(l.split()[12]) for l in subprocess.run(['pdfimages', '-list', '-l', '30', SCAN], cwd=work, capture_output=True, text=True).stdout.split('\n')[2:]
           if len(l.split()) > 13 and l.split()[2] in ('image', 'mask', 'smask', 'stencil')]
    DPI = str(int(min(400, max(72, round(max(ppi))))) if ppi else 300)
DPI = DPI or '300'
if SCAN.endswith('.pdf') and len(_src) in (3, 4): open(f'{work}/provenance/source.txt', 'w').write(' '.join(_src[:3] + [DPI]) + '\n')
# ESZETT=ſs: the print has no ß type and sets ſs for it everywhere (checked on the scans)
ESZETT = os.environ.get('ESZETT', '')      # ESZETT=auto: decided from the recognition of the whole work (see below)
# LONGS=0: the print has no long s (modern Antiqua); a long s read by the models counts as s
LONGS = os.environ.get('LONGS', '1') != '0'
MAXSUBST = int(os.environ.get('MAXSUBST', '2'))
# STRICT=1: a line is left out when both models read the same other letter where
# Wikisource was taken (the transcription then often differs from the print)
STRICT = os.environ.get('STRICT', '0') == '1'
SUBS = []                 # places of the last successful hybrid(): (position in wu, letter read)
# forms where the recognition is not trusted and Wikisource is taken: (recognised, Wikisource)
TAKE_WS = {('ʒ', 'z'), ('ũ', 'ü'), ('·', '/'), ('u\u0366', 'ü'), ('ü', 'u\u0366'), ('ı', 'i'), ('J', 'I'), ('I', 'J'), ('v', 'u'), ('u', 'v')} - {('v', 'u'), ('u', 'v')}

def uo(s):
    """u with small o above in the OCR-D form: u + U+0366 COMBINING LATIN SMALL
    LETTER O. Wikisource and the models (trained on GT4HistOCR) also write
    U+016F LATIN SMALL LETTER U WITH RING ABOVE for it."""
    return s.replace('ů', 'u\u0366').replace('Ů', 'U\u0366')

def units(s):
    out = []
    for c in uo(unicodedata.normalize('NFC', s)):
        if out and unicodedata.combining(c): out[-1] = unicodedata.normalize('NFC', out[-1] + c)
        else: out.append(c)
    return out

def skeleton(s):
    s = unicodedata.normalize('NFD', s.replace('ſ', 's').replace('ꝛ', 'r').replace('ʒ', 'z').lower())
    return ''.join(c for c in s if c.isalnum())

unknown_templates = collections.Counter()
def ws_lines(wikitext):
    """printed lines of a page from the wikitext: [(text, usable)]"""
    t = re.sub(r'<noinclude>.*?</noinclude>', '', wikitext, flags=re.S)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    def printed(m):                     # word<ref>''Vorlage:'' printed form</ref>
        v = m.group(2).strip(); k = len(v.split()); words = m.group(1).split(' ')
        return ' '.join(words[:-k] + [v])
    t = re.sub(r"((?:[^\s<>]+ ){0,3}[^\s<>]+)<ref[^>]*>\s*''Vorlage:''\s*([^<]*?)</ref>", printed, t)
    t = re.sub(r'<ref[^>]*>.*?</ref>|<ref[^>]*/>', '⟦⟧', t, flags=re.S)
    t = re.sub(r'<sup>e</sup>', 'ͤ', t); t = re.sub(r'<sup>o</sup>', 'ͦ', t)
    t = uo(t)
    t = re.sub(r'<br\s*/?>', '\n', t)
    def template(m):
        parts = m.group(1).split('|'); n = parts[0].strip()
        if n in ('BRU', 'PRZU', 'Seite', 'SeitePR', 'Anker', 'NotTOC', 'LineCenterSize', 'References', 'LeereSeite', 'Linie', 'idt2', 'Idt2',
                 'NotizLinks', 'NotizRechts', 'BlockSatzStart', 'BlockSatzEnd'):      # images, anchors, indents, rules; marginal notes are not part of the text line
            return '\n' if n in ('BRU', 'Linie') else ''
        if n == 'sup':                              # {{sup|e}}: small letter above the letter before
            return {'e': '\u0364', 'o': '\u0366'}.get(parts[-1].strip(), '⟦⟧')
        if n in ('Unicode', 'Polytonisch', 'Dropinitial', 'Headline', 'An', 'left', 'Initiale', 'Center', 'center', 'idt', 'Idt', 'SperrSchrift', 'Sperrschrift', 'Kapitaelchen', 'Kapitälchen', 'Zeile', 'right', 'Right', 'larger', 'smaller', 'ss', 'nowrap', 'Nowrap'):
            return parts[-1] if n not in ('idt', 'Idt', 'Zeile') else ''
        unknown_templates[n] += 1; return '⟦⟧'
    for _ in range(3): t = re.sub(r'\{\{([^{}]*)\}\}', template, t)
    t = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', t)
    t = re.sub(r"'{2,}", '', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('&nbsp;', ' ')
    out = []
    for l in t.split('\n'):
        l = unicodedata.normalize('NFC', ' '.join(l.split()))
        if not l or l.startswith(('{|', '|}', '|-', '__')): continue
        l = re.sub(r'^[:;*#]+ *', '', l)
        if l: out.append((l, '⟦' not in l and '{' not in l and '}' not in l))
    return out

def ocr(png, model, n):
    xml = f'{work}/.ocr/{n:04d}.{model}.page.xml'
    if not os.path.exists(xml):
        subprocess.run([T, png, xml[:-9], '--tessdata-dir', TESSDATA, '-l', model, '--psm', '3', '-c', 'tessedit_create_page_xml=1'],
                       capture_output=True, env=dict(os.environ, OMP_THREAD_LIMIT='1'), check=True)
    return xml

def page_lines(xml):
    """[(line id, text, outline)] in the order of the file, and the tree"""
    tree = ET.parse(xml); res = []
    for tl in tree.iter(q('TextLine')):
        u = tl.find(f'{q("TextEquiv")}/{q("Unicode")}')
        c = tl.find(q('Coords'))
        res.append((tl.get('id'), unicodedata.normalize('NFC', (u.text or '') if u is not None else ''), c.get('points') if c is not None else tl.get('id')))
    return res, tree

def skel_units(us):
    """skeleton character for every unit ('' for units without one)"""
    return [skeleton(u)[:1] for u in us]

def hybrid(ou, wu):
    """ou: units of the recognised line without blanks; wu: units of a stretch
    of the Wikisource text. Returns (text, None) with the letters of Wikisource
    and the print forms of the recognition, or (None, reason)."""
    out = []; i = 0; j = 0; subst = 0; subs = []
    while j < len(wu):
        if wu[j] == ' ': out.append(' '); j += 1; continue
        if i >= len(ou): return None, 'recognition ends early'
        x = ou[i]
        if x == wu[j]: out.append(x); i += 1; j += 1; continue
        done = False
        for e in PAIRS.get(x, []):
            k = j
            for c in e:
                if k < len(wu) and wu[k] == c: k += 1
                else: break
            else:
                out.append(x); i += 1; j = k; done = True; break
        if done: continue
        if x == 'ſ' and wu[j] == 'ß' and i + 1 < len(ou) and ou[i + 1] == 's': out.append('ſs'); i += 2; j += 1; continue   # ſs set as two letters
        if (x, wu[j]) in TAKE_WS: out.append(wu[j]); i += 1; j += 1; continue
        # f and long s are easily confused by the models: the letter is decided by Wikisource
        if (x, wu[j]) == ('ſ', 'f'): out.append('f'); i += 1; j += 1; continue
        if (x, wu[j]) == ('f', 's') and j + 1 < len(wu) and wu[j + 1] != ' ': out.append('ſ'); i += 1; j += 1; continue
        # One letter read as another letter: Wikisource is taken (at most MAXSUBST
        # per line). Not for a recognised print form whose expansion did not fit,
        # and only when the letters after it agree again.
        if (subst < MAXSUBST and x not in NOSUBST and x[0].isalpha() and wu[j][0].isalpha() and i + 1 < len(ou) and j + 1 < len(wu)
                and wu[j + 1] != ' ' and (ou[i + 1] == wu[j + 1] or wu[j + 1] in PAIRS.get(ou[i + 1], [''])[0][:1] or (ou[i + 1], wu[j + 1]) == ('ſ', 's'))):
            subs.append((j, x)); out.append(wu[j]); i += 1; j += 1; subst += 1; continue
        return None, f'differs: "{"".join(ou[max(0, i - 3):i + 4])}" against "{"".join(wu[max(0, j - 3):j + 4])}"'
    if i < len(ou): return None, 'recognition has more'
    SUBS[:] = subs
    return ''.join(out).replace('z', ZFORM), None

virg = lambda s: re.sub(r' */ *', '/ ', s).strip()

def assign(lines, wu, boxes):
    """For every recognised line the stretch of the Wikisource text wu (units,
    whole page) which gives a text without unexplained difference:
    {line index: (text, start, end)} and {line index: reason}"""
    lu = [[x for x in units(virg(t if LONGS else t.replace('ſ', 's'))) if x != ' '] for t in lines]
    hyph = []
    for u in lu:                                   # hyphen at the line end: kept apart
        h = ''
        if len(u) > 1 and u[-1] in '⸗-=': h = u.pop()
        hyph.append(h)
    stream = []; owner = []
    for i, u in enumerate(lu):
        for x in u:
            for c in skeleton(x): stream.append(c); owner.append(i)
    wsk = []; wpos = []
    for k, x in enumerate(wu):
        for c in skeleton(x): wsk.append(c); wpos.append(k)
    guess = {}                                     # line -> (first, last) matched position in wu
    for b in difflib.SequenceMatcher(None, stream, wsk, autojunk=False).get_matching_blocks():
        for k in range(b.size):
            i = owner[b.a + k]; p = wpos[b.b + k]
            guess[i] = (guess[i][0], p) if i in guess else (p, p)
    res = {}; why = {}; prev_end = None; assign.subs = subs = {}
    for i, u in enumerate(lu):
        if i not in guess or len(u) < 2: why[i] = 'no text of Wikisource found'; prev_end = None; continue
        g0, g1 = guess[i]
        starts = [prev_end] if prev_end is not None else []
        starts += [x for x in range(max(0, g0 - 6), min(len(wu), g0 + 4)) if x not in starts]
        best = None; reason = None
        for s0 in starts:
            while s0 < len(wu) and wu[s0] == ' ': s0 += 1
            for e in range(min(len(wu), g1 + 8), max(s0 + 1, g1 - 4) - 1, -1):      # longest first: an abbreviation at the line end takes its whole expansion
                if wu[e - 1] == ' ': continue
                t, r = hybrid(u, wu[s0:e])
                if t is not None: best = (t, s0, e); found = {(s0 + j, x) for j, x in SUBS}; break
                if reason is None or r.startswith('differs'): reason = reason if (reason or '').startswith('differs') else r
            if best: break
        if not best: why[i] = reason or 'no stretch fits'; prev_end = None; continue
        t, s0, e = best
        if '⟧' in wu[max(0, s0 - 2):s0] or '⟦' in wu[e:e + 2]:    # the print may have a footnote mark there which the recognition missed
            why[i] = 'beside a footnote mark or an unknown template'; prev_end = None; continue
        inword = e < len(wu) and wu[e] != ' ' and wu[e] != '⟦'
        if hyph[i]:
            if not inword: why[i] = 'hyphen at the line end, but the word ends in Wikisource'; prev_end = e; continue
            t += hyph[i]
        res[i] = (t, s0, e); subs[i] = found; prev_end = e
    # The layout analysis sometimes cuts a printed line into pieces. A piece
    # which starts or ends inside a word is not used: its image shows a cut
    # word. A piece is recognised by a neighbour on the same row close to that
    # side. Without such a neighbour the line stands alone, and a text which
    # starts or ends inside a word is a real line break of the print (early
    # prints split words without a hyphen), or the start is an initial outside
    # the line. With a neighbour, the text is still right if the other part of
    # the word is the text of a used line on another row.
    def apart(a, b):
        ov = min(a[3], b[3]) - max(a[1], b[1])
        return ov < 0.5 * min(a[3] - a[1], b[3] - b[1])
    def neighbour(i, left):
        a = boxes[i]; h = a[3] - a[1]
        for k, b in enumerate(boxes):
            if k == i or apart(a, b): continue
            gap = a[0] - b[2] if left else b[0] - a[2]
            if -h < gap < 3 * h and (b[0] < a[0] if left else b[2] > a[2]): return True
        return False
    changed = True
    while changed:
        changed = False
        for i, (t, s0, e) in list(res.items()):
            if (s0 > 0 and wu[s0 - 1] not in ' ⟦⟧' and neighbour(i, True)
                    and not any(res[p][2] == s0 and apart(boxes[i], boxes[p]) for p in res if p != i)):
                why[i] = 'piece of a line: starts inside a word'; del res[i]; changed = True; continue
            if (e < len(wu) and wu[e] not in ' ⟦⟧' and not hyph[i] and neighbour(i, False)
                    and not any(res[n][1] == e and apart(boxes[i], boxes[n]) for n in res if n != i)):
                why[i] = 'piece of a line: ends inside a word'; del res[i]; changed = True
    return res, why

os.makedirs(f'{work}/.ocr', exist_ok=True); os.makedirs(f'{work}/GT-PAGE', exist_ok=True)
pagefiles = sorted(glob.glob(f'{work}/provenance/wikisource/*.json'), key=lambda p: int(os.path.basename(p)[:-5]))

def page_image(n, base):
    png = f'{work}/GT-PAGE/{base}.png'
    if not SCAN: png = (glob.glob(f'{work}/GT-PAGE/{base}.jpg') + glob.glob(f'{work}/GT-PAGE/{base}.png') + [png])[0]
    for attempt in range(8):            # ImageMagick sometimes fails on a DjVu page ("recursive opening"); a retry helps
        if os.path.exists(png) and os.path.getsize(png): return png
        if not SCAN: continue
        if SCAN.endswith('.pdf'):
            r = subprocess.run(['pdftoppm', '-r', DPI, '-gray', '-png', '-f', str(n), '-l', str(n), '-singlefile', SCAN, os.path.abspath(png)[:-4]], cwd=work, capture_output=True)
        else:
            r = subprocess.run(['convert', f'{SCAN}[{n - 1}]', os.path.abspath(png)], cwd=work, capture_output=True)
        if r.returncode and os.path.exists(png): os.remove(png)
    return None

if ESZETT == 'auto':
    # Does the print have a ß type? Count ß in Wikisource and what the first model reads on the same pages.
    ws_n = oc = ls = 0
    for f in pagefiles:
        d = json.load(open(f, encoding='utf-8')); n = d['page']
        if d['level'] < 3 or not first <= n <= last: continue
        png = page_image(n, f'{name}_{n:04d}')
        if not png: continue
        t = ' '.join(x[1] for x in page_lines(ocr(png, M1, n))[0])
        ws_n += d['wikitext'].count('ß'); oc += t.count('ß'); ls += t.count('ſs')
    ESZETT = '' if ws_n < 20 or oc >= 0.3 * ws_n else 'ſs' if ls >= 0.3 * ws_n else 'ss'
    print('ß in Wikisource', ws_n, '| read as ß', oc, '| read as ſs', ls, '| ESZETT =', repr(ESZETT), flush=True)
stat = collections.Counter(); reasons = collections.Counter(); rows = []
for f in pagefiles:
    d = json.load(open(f, encoding='utf-8')); n = d['page']
    if not first <= n <= last: continue
    if d['level'] < 3: stat['pages not proofread'] += 1; continue
    ws = ws_lines(d['wikitext'])
    if not ws: stat['pages without text'] += 1; continue
    base = f'{name}_{n:04d}'; png = page_image(n, base)
    if not png: stat['pages without image'] += 1; print(n, 'no image'); continue
    (l1, tree), (l2, _) = page_lines(ocr(png, M1, n)), page_lines(ocr(png, M2, n))
    # A text line with a footnote mark or an unknown template keeps its text, with ⟦⟧
    # at that place: in modern works a whole paragraph is one line of wikitext.
    wu = units(virg(' '.join(w if usable or ('{' not in w and '}' not in w) else '⟦⟧' for w, usable in ws)))
    if ESZETT: wu = units(''.join(wu).replace('ß', ESZETT))
    def box(points):
        xy = [tuple(map(int, p.split(','))) for p in points.split()]
        return min(x for x, _ in xy), min(y for _, y in xy), max(x for x, _ in xy), max(y for _, y in xy)
    def iou(a, b):
        w = min(a[2], b[2]) - max(a[0], b[0]); h = min(a[3], b[3]) - max(a[1], b[1])
        if w <= 0 or h <= 0: return 0
        return w * h / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - w * h)
    b1 = [box(x[2]) for x in l1]; b2 = [box(x[2]) for x in l2]
    r1, y1 = assign([x[1] for x in l1], wu, b1); s1 = assign.subs; r2, y2 = assign([x[1] for x in l2], wu, b2); s2 = assign.subs
    def second(points):                 # the same line of the second model: nearly the same box
        a = box(points); k = max(range(len(b2)), key=lambda k: iou(a, b2[k]), default=None)
        return k if k is not None and iou(a, b2[k]) > 0.7 else None
    keep = {}; dropped = {}; stat['pages'] += 1; stat['Wikisource lines'] += len(ws); stat['recognised lines'] += len(l1)
    for i, (lid, t1, outline) in enumerate(l1):
        k = second(outline); t2 = l2[k][1] if k is not None else ''
        if i not in r1: why = y1[i]
        elif k is None: why = 'second model has no such line'
        elif k not in r2: why = 'second model: ' + y2[k]
        elif r1[i] != r2[k]: why = 'models differ'
        elif STRICT and s1.get(i, set()) & s2.get(k, set()): why = 'both models read another letter than Wikisource'
        else: why = None; keep[lid] = r1[i][0]
        group = 'used' if why is None else 'left out'
        stat['lines ' + group] += 1
        if why: reasons[why.split(': "')[0]] += 1
        span = ''.join(wu[r1[i][1]:r1[i][2]]) if i in r1 else ''
        rows.append('\t'.join([base, lid, group, why or '', span, t1.strip(), t2.strip(), keep.get(lid, '')]))
        if why: dropped[lid] = (why, span, t1, t2)
    # PAGE file: lines with text, regions without lines removed
    page = tree.getroot().find(q('Page')); page.set('imageFilename', os.path.basename(png))
    # Lines which are left out stay in the file as XML comments (place, reason,
    # the stretch of Wikisource if one was found, both recognitions), so that
    # nothing is lost and they can be completed by hand.
    cm = lambda t: re.sub(r"-(?=-)", "- ", t)
    for reg in list(page.iter(q('TextRegion'))):
        texts = []
        for pos, tl in enumerate(list(reg)):
            if tl.tag != q('TextLine'): continue
            lid = tl.get('id')
            if lid not in keep:
                why, span, t1, t2 = dropped.get(lid, ('', '', '', ''))
                c = tl.find(q('Coords')); b = tl.find(q('Baseline'))
                note = ET.Comment(cm(f' line left out: id="{lid}" points="{c.get("points") if c is not None else ""}" '
                                     f'baseline="{b.get("points") if b is not None else ""}" reason: {why} | Wikisource: {span} | {M1}: {t1} | {M2}: {t2} '))
                note.tail = tl.tail; reg.insert(list(reg).index(tl), note); reg.remove(tl); continue
            for wd in tl.findall(q('Word')): tl.remove(wd)
            te = tl.find(q('TextEquiv')); te.attrib.pop('conf', None); te.find(q('Unicode')).text = keep[lid]; texts.append(keep[lid])
        te = reg.find(q('TextEquiv'))
        if te is not None:
            if texts: te.attrib.pop('conf', None); te.find(q('Unicode')).text = '\n'.join(texts)
            else: reg.remove(te)
    page.append(ET.Comment(cm(' Wikisource text of the page (normalised spelling, see the README):\n' + '\n'.join(w for w, _ in ws) + '\n')))
    md = tree.getroot().find(q('Metadata'))
    md.find(q('Creator')).text = 'ws-build.py (Wikisource text, line coordinates from Tesseract)'
    c = md.find(q('Comments'))
    if c is None: c = ET.SubElement(md, q('Comments'))
    c.text = (f'Text: https://{d["site"]}/wiki/{d["title"].replace(" ", "_")} revision {d["revid"]} of {d["timestamp"]}, '
              f'proofread level {d["level"]}, licence CC BY-SA 4.0. Long s, r rotunda and abbreviation marks restored from '
              f'the recognition with {M1} and {M2}; lines where the two disagree or differ from Wikisource are left out and kept as comments.')
    if keep:
        ET.indent(tree, '\t'); tree.write(f'{work}/GT-PAGE/{base}.xml', encoding='UTF-8', xml_declaration=True); stat['PAGE files'] += 1
    print(n, len(l1), 'lines,', len(keep), 'used', flush=True)
open(f'{work}/provenance/lines.tsv', 'w', encoding='utf-8').write('page\tline\tgroup\treason\tWikisource\t' + M1 + '\t' + M2 + '\ttext\n' + '\n'.join(rows) + '\n')
json.dump({'models': [M1, M2], 'zform': ZFORM, 'eszett': ESZETT, 'longs': LONGS, **stat, 'left out': dict(reasons)}, open(f'{work}/provenance/build.json', 'w'), ensure_ascii=False, indent=1)
print(dict(stat)); print('left out:', reasons.most_common()); print('unknown templates:', unknown_templates.most_common())
