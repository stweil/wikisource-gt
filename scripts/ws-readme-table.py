#!/usr/bin/env python3
"""Rewrite the table of works in README.md from the work.yml files.
usage (in the repository root): scripts/ws-readme-table.py"""
import glob, json, subprocess
def read(f):
    y = {}
    for l in open(f, encoding='utf-8'):
        k, v = l.rstrip('\n').split(': ', 1); y[k] = json.loads(v) if v.startswith('"') else v
    return y
works = sorted(((read(f), '/'.join(f.split('/')[1:3])) for f in glob.glob('data/*/*/work.yml')
               if subprocess.run(['git', 'check-ignore', '-q', f]).returncode)   # works which git ignores are not ready
              , key=lambda x: (x[0]['year'], x[1]))
tot = [0, 0, 0]; rows = []
for y, d in works:
    p, u, o = int(y['pages']), int(y['lines-used']), int(y['lines-left-out']); tot[0] += p; tot[1] += u; tot[2] += o
    rows.append('| `%s` | %s | %s | %s | %s |' % (d, y['title'], f'{p:,}', f'{u:,}', f'{o:,}'))
tab = '| Directory | Work | Pages | Lines used | Lines left out |\n|---|---|---|---|---|\n' + '\n'.join(rows) + '\n| | **Total** | **%s** | **%s** | **%s** |' % tuple(f'{t:,}' for t in tot)
s = open('README.md', encoding='utf-8').read()
i = min(k for k in (s.find('| Work | Year | Pages'), s.find('| Directory | Work | Pages')) if k >= 0); j = s.index('\n\n', i)
open('README.md', 'w', encoding='utf-8').write(s[:i] + tab + s[j:])
print(tab)
