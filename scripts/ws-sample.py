#!/usr/bin/env python3
"""Sample sheet for checking: N random used lines of a work, each line image
above its number; the texts are printed.

usage: ws-sample.py WORKDIR N OUT.jpg [SEED]"""
import glob, os, random, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
work, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]; random.seed(int(sys.argv[4]) if len(sys.argv) > 4 else 1)
NS = '{http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15}'
lines = []
for f in sorted(glob.glob(work + '/GT-PAGE/*.xml')):
    t = ET.parse(f); img = os.path.dirname(f) + '/' + t.getroot().find(NS + 'Page').get('imageFilename')
    for tl in t.iter(NS + 'TextLine'):
        p = [tuple(map(int, x.split(','))) for x in tl.find(NS + 'Coords').get('points').split()]
        lines.append((img, min(x for x, _ in p), min(y for _, y in p), max(x for x, _ in p), max(y for _, y in p),
                      tl.find(NS + 'TextEquiv').find(NS + 'Unicode').text, os.path.basename(f)[:-4] + ' ' + tl.get('id')))
with tempfile.TemporaryDirectory() as tmp:
    parts = []
    for k, (img, x0, y0, x1, y1, text, where) in enumerate(random.sample(lines, min(n, len(lines))), 1):
        p = f'{tmp}/{k}.png'
        subprocess.run(['convert', img, '-crop', f'{x1 - x0 + 8}x{y1 - y0 + 8}+{max(0, x0 - 4)}+{max(0, y0 - 4)}', '+repage', '-resize', '1300x', '-background', 'white',
                        '-gravity', 'west', '-extent', '1300x', p], check=True)
        parts.append(p); print(f'{k}: {text}    [{where}]')
    subprocess.run(['convert'] + parts + ['-background', 'white', '-splice', '0x14', '-append', '-quality', '80', out], check=True)
