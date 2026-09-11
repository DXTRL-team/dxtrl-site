#!/usr/bin/env python3
"""Check deployable pages, internal links, images, headings and ARIA references."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
errors = []

class Page(HTMLParser):
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.ids = set()
        self.refs = []
        self.local_ids = []
        self.h1 = 0
        self.title = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids: errors.append(f'{self.file}: duplicate id {a["id"]}')
            self.ids.add(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.title += 1
        if tag == 'img' and 'alt' not in a: errors.append(f'{self.file}: image missing alt')
        if tag == 'iframe' and not a.get('title'): errors.append(f'{self.file}: iframe missing title')
        if tag == 'video':
            for required in ('muted', 'playsinline', 'poster', 'aria-label', 'aria-describedby'):
                if required not in a: errors.append(f'{self.file}: video missing {required}')
            if not a.get('data-src'): errors.append(f'{self.file}: video missing lazy source')
        for key in ('href', 'src', 'poster', 'data-src'):
            if a.get(key): self.refs.append(a[key])
        for key in ('aria-controls', 'aria-labelledby', 'aria-describedby', 'for'):
            self.local_ids.extend(a.get(key, '').split())
        if a.get('target') == '_blank' and 'noopener' not in a.get('rel', ''):
            errors.append(f'{self.file}: external tab missing noopener')

pages = {}
for file in sorted(DIST.rglob('*.html')):
    page = Page(file.relative_to(DIST)); text = file.read_text(); page.feed(text); pages[file.resolve()] = page
    if page.h1 != 1 or page.title != 1: errors.append(f'{page.file}: expected one h1/title, found {page.h1}/{page.title}')
    if 'api.studiodesignapp.com' in text: errors.append(f'{page.file}: obsolete dependency')
    if '{{' in text: errors.append(f'{page.file}: unresolved template')

for file, page in pages.items():
    for ident in page.local_ids:
        if ident not in page.ids: errors.append(f'{page.file}: missing ARIA/label target {ident}')
    for ref in page.refs:
        u = urlsplit(ref)
        if u.netloc in ('dxtrl.com', 'www.dxtrl.com'): errors.append(f'{page.file}: old corporate link {ref}')
        if u.netloc or u.scheme: continue
        target = (DIST / unquote(u.path).lstrip('/')) if u.path.startswith('/') else (file.parent / unquote(u.path))
        if not u.path: target = file
        if target.is_dir(): target /= 'index.html'
        target = target.resolve()
        if not target.exists(): errors.append(f'{page.file}: missing local target {ref}')
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
            errors.append(f'{page.file}: missing fragment {ref}')

for a in json.loads((ROOT / 'src/content/articles.json').read_text()):
    target = DIST / a['path'].lstrip('/') / 'index.html'
    if not target.exists(): errors.append(f'Missing original article route {a["path"]}')

css = '\n'.join(p.read_text() for p in DIST.glob('*.css'))
for url in re.findall(r'url\([\"\']?([^\)\"\']+)', css):
    if url.startswith('/') and not (DIST / url.lstrip('/')).exists(): errors.append(f'CSS missing asset {url}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {len(pages)} pages; internal routes/fragments, local assets, headings, ARIA, original article coverage.')
print('PASS: labeled, muted concept-video references; no legacy corporate hrefs or Studio submission dependency.')
