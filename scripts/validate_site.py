#!/usr/bin/env python3
"""Check deployable pages, internal links, images, headings and ARIA references."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree
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
        self.canonical = []
        self.social_urls = []
        self.schema = []
        self._json = None
        self._in_main = False
        self.heading_levels = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'main':
            self._in_main = True
        if self._in_main and tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.heading_levels.append(int(tag[1]))
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical.append(a.get('href'))
        if tag == 'meta' and a.get('property') == 'og:url':
            self.social_urls.append(a.get('content'))
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self._json = []
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
            if tag == 'link' and key == 'href' and a.get('rel') == 'canonical':
                continue
            if a.get(key): self.refs.append(a[key])
        for key in ('aria-controls', 'aria-labelledby', 'aria-describedby', 'for'):
            self.local_ids.extend(a.get(key, '').split())
        if a.get('target') == '_blank' and 'noopener' not in a.get('rel', ''):
            errors.append(f'{self.file}: external tab missing noopener')

    def handle_data(self, data):
        if self._json is not None:
            self._json.append(data)

    def handle_endtag(self, tag):
        if tag == 'main':
            self._in_main = False
        if tag == 'script' and self._json is not None:
            try:
                data = json.loads(''.join(self._json))
                self.schema.extend(data.get('@graph', [data]))
            except (ValueError, AttributeError) as exc:
                errors.append(f'{self.file}: invalid JSON-LD: {exc}')
            self._json = None

pages = {}
for file in sorted(DIST.rglob('*.html')):
    page = Page(file.relative_to(DIST)); text = file.read_text(); page.feed(text); pages[file.resolve()] = page
    if page.h1 != 1 or page.title != 1: errors.append(f'{page.file}: expected one h1/title, found {page.h1}/{page.title}')
    if 'api.studiodesignapp.com' in text: errors.append(f'{page.file}: obsolete dependency')
    if '{{' in text: errors.append(f'{page.file}: unresolved template')

origin = 'https://dxtrl.com'
canonical_urls = set()
for file, page in pages.items():
    if file.name == 'index.html':
        rel = file.parent.relative_to(DIST)
        expected = origin + '/' + (rel.as_posix() + '/' if rel.parts else '')
        canonical_urls.add(expected)
        if page.canonical != [expected] or page.social_urls != [expected]:
            errors.append(f'{page.file}: expected one matching canonical and og:url ({expected})')
    elif page.canonical or page.social_urls:
        errors.append(f'{page.file}: non-index page must not declare a canonical URL')
    if page.file.as_posix() in ('news/index.html', 'news/category/press/index.html', 'news/category/notice/index.html'):
        levels = page.heading_levels
        if any(b > a + 1 for a, b in zip(levels, levels[1:])):
            errors.append(f'{page.file}: heading level skipped')

locations = [n.text for n in ElementTree.parse(DIST / 'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
if set(locations) != canonical_urls or len(locations) != len(canonical_urls):
    errors.append('Sitemap entries must match unique canonical URLs')
if {v.get('@type') for v in pages[(DIST / 'index.html').resolve()].schema} != {'Organization', 'WebSite'}:
    errors.append('Home requires Organization and WebSite JSON-LD')
if [v.get('@type') for v in pages[(DIST / 'dealer-ax/index.html').resolve()].schema] != ['Service']:
    errors.append('Dealer AX requires its existing Service JSON-LD')

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
    if not target.exists():
        errors.append(f'Missing original article route {a["path"]}')
        continue
    expected = origin + a['path'] + '/'
    schema = [v for v in pages[target.resolve()].schema if v.get('@type') == 'Article']
    if (len(schema) != 1 or schema[0].get('headline') != a['title']
            or schema[0].get('datePublished') != a['date'].replace('.', '-')
            or schema[0].get('url') != expected):
        errors.append(f'{a["path"]}: article JSON-LD does not match the visible title, date, and URL')

css = '\n'.join(p.read_text() for p in DIST.glob('*.css'))
for url in re.findall(r'url\([\"\']?([^\)\"\']+)', css):
    if url.startswith('/') and not (DIST / url.lstrip('/')).exists(): errors.append(f'CSS missing asset {url}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {len(pages)} pages; internal routes/fragments, local assets, headings, ARIA, original article coverage.')
print('PASS: labeled, muted concept-video references; no legacy corporate hrefs or Studio submission dependency.')

print('PASS: canonical URLs, sitemap, social URLs, news heading levels, and JSON-LD for home, Dealer AX and all articles.')
