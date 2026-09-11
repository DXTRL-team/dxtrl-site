#!/usr/bin/env python3
"""Create a GitHub Pages artifact for both a project subpath and a custom domain."""
import argparse
import re
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--base-path', default='')
args = parser.parse_args()
base = '/' + args.base_path.strip('/') if args.base_path.strip('/') else ''
if base and not re.fullmatch(r'/[A-Za-z0-9._/-]+', base):
    parser.error('Unexpected base path')
out = root / 'pages-dist'
if out.exists(): shutil.rmtree(out)
shutil.copytree(root / 'dist', out)
for path in out.rglob('*.html'):
    text = path.read_text()
    text = re.sub(r'((?:href|src|poster)=")/(?!/)', lambda m: m.group(1) + base + '/', text)
    path.write_text(text)
print(f'Prepared GitHub Pages artifact with base path {base or "/"}')
