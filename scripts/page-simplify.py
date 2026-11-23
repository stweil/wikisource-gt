#!/usr/bin/env python3
"""Reduce the points of the line polygons and baselines in PAGE XML files.

usage: page-simplify.py [--eps PIXELS] [--dry] PAGE.xml...   (default --eps 2)

Douglas-Peucker: a point is dropped when it lies within EPS pixels of the
straight line between the points which are kept. For every `TextLine` the
`points` of its `Coords` (a closed polygon) and of its `Baseline` (an open
line) are reduced. The points which give the bounding box of polygon and
baseline together are always kept, so the box of the line (and with it a
line image cut by the box) stays exactly the same; this is checked for every
line. Only the two `points` attributes change; every other byte of the file
stays. Prints the number of points and the size of the files before and after.
"""
import os, re, sys
args = sys.argv[1:]; eps = 2.0; dry = False
while args and args[0].startswith('--'):
    a = args.pop(0)
    if a == '--eps': eps = float(args.pop(0))
    elif a == '--dry': dry = True
def pts(s): return [tuple(int(float(v)) for v in p.split(',')) for p in s.split()]
def fmt(q): return ' '.join(f'{x},{y}' for x, y in q)
def dist(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b; dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0: return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return ((x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2) ** 0.5
def dp(q, keep, i, j):
    """mark the points of q[i..j] which must stay (i and j are kept already)"""
    stack = [(i, j)]
    while stack:
        i, j = stack.pop()
        if j - i < 2: continue
        k, d = max(((k, dist(q[k], q[i], q[j])) for k in range(i + 1, j)), key=lambda v: v[1])
        if d > eps: keep[k] = True; stack += [(i, k), (k, j)]
def reduce(q, box, closed):
    n = len(q)
    if n < 3: return q
    keep = [False] * n
    for k, (x, y) in enumerate(q):
        if x in (box[0], box[2]) or y in (box[1], box[3]): keep[k] = True      # points on the bounding box
    if closed:
        if not any(keep): keep[0] = True
        first = keep.index(True); q = q[first:] + q[:first]; keep = keep[first:] + keep[:first]      # start at a kept point
        q2 = q + [q[0]]; keep2 = keep + [True]
    else:
        keep[0] = keep[-1] = True; q2, keep2 = q, keep
    anchors = [k for k, v in enumerate(keep2) if v]
    for a, b in zip(anchors, anchors[1:]): dp(q2, keep2, a, b)
    r = [p for p, v in zip(q2, keep2) if v]
    if closed: r = r[:-1]
    out = [r[0]]
    for p in r[1:]:
        if p != out[-1]: out.append(p)
    return out if len(out) >= (3 if closed else 2) else q
LINE = re.compile(r'<TextLine\b[^>]*>')
COORDS = re.compile(r'(<Coords\b[^>]*\bpoints=")([^"]*)(")')
BASE = re.compile(r'(<Baseline\b[^>]*\bpoints=")([^"]*)(")')
tot = dict(files=0, lines=0, poly_before=0, poly_after=0, base_before=0, base_after=0, bytes_before=0, bytes_after=0, bad=0)
for xml in args:
    s = open(xml, encoding='utf-8', newline='').read(); edits = []
    for m in LINE.finditer(s):
        end = s.find('</TextLine>', m.end()); w = s.find('<Word', m.end(), end); stop = end if w < 0 else w
        c = COORDS.search(s, m.end(), stop); b = BASE.search(s, m.end(), stop)
        if c is None or not c.group(2).strip(): continue
        q = pts(c.group(2)); bq = pts(b.group(2)) if b and b.group(2).strip() else []
        al = q + bq; box = (min(p[0] for p in al), min(p[1] for p in al), max(p[0] for p in al), max(p[1] for p in al))
        nq = reduce(q, box, True); nb = reduce(bq, box, False) if bq else []
        al2 = nq + nb; box2 = (min(p[0] for p in al2), min(p[1] for p in al2), max(p[0] for p in al2), max(p[1] for p in al2))
        tot['lines'] += 1
        if box2 != box: tot['bad'] += 1; print('box would change, line left:', xml, m.group(0)[:60]); nq, nb = q, bq
        tot['poly_before'] += len(q); tot['poly_after'] += len(nq); tot['base_before'] += len(bq); tot['base_after'] += len(nb)
        if nq != q: edits.append((c.start(2), c.end(2), fmt(nq)))
        if bq and nb != bq: edits.append((b.start(2), b.end(2), fmt(nb)))
    out = []; pos = 0
    for a, e, t in sorted(edits): out.append(s[pos:a]); out.append(t); pos = e
    out.append(s[pos:]); ns = ''.join(out)
    tot['files'] += 1; tot['bytes_before'] += len(s.encode('utf-8')); tot['bytes_after'] += len(ns.encode('utf-8'))
    if not dry and ns != s: open(xml, 'w', encoding='utf-8', newline='').write(ns)
t = tot
print(f"eps {eps:g}: {t['files']} files, {t['lines']} lines; polygon points {t['poly_before']} -> {t['poly_after']} "
      f"({t['poly_before'] / max(1, t['lines']):.1f} -> {t['poly_after'] / max(1, t['lines']):.1f} per line); "
      f"baseline points {t['base_before']} -> {t['base_after']} ({t['base_before'] / max(1, t['lines']):.1f} -> {t['base_after'] / max(1, t['lines']):.1f}); "
      f"size {t['bytes_before'] / 1e6:.2f} MB -> {t['bytes_after'] / 1e6:.2f} MB ({100 - 100 * t['bytes_after'] / max(1, t['bytes_before']):.1f} % less); lines left because of the box: {t['bad']}")
