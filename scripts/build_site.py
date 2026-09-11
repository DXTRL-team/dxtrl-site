#!/usr/bin/env python3
"""Build the DXTRL static site with the Python standard library only."""
import html
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
OUT = ROOT / 'dist'
E = html.escape

def local_link(url):
    parsed = urlsplit(url)
    if parsed.netloc in ('dxtrl.com', 'www.dxtrl.com'):
        path = parsed.path or '/'
        if not Path(path).suffix and not path.endswith('/'):
            path += '/'
        return urlunsplit(('', '', path, parsed.query, parsed.fragment))
    return url

class ArticleHTML(HTMLParser):
    """Keep public article text, headings, links and images; drop source UI attributes."""
    tags = {'p', 'strong', 'b', 'em', 'i', 'u', 's', 'br', 'a', 'img', 'h2', 'h3', 'h4',
            'ul', 'ol', 'li', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'figure', 'figcaption', 'hr', 'span', 'div'}
    void = {'br', 'img', 'hr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if self.skip or tag not in self.tags:
            return
        attrs = dict(attrs)
        clean = {}
        if attrs.get('id'):
            clean['id'] = attrs['id']
        if tag == 'a' and attrs.get('href'):
            url = local_link(attrs['href'])
            if urlsplit(url).scheme in ('', 'https', 'http', 'mailto', 'tel'):
                clean['href'] = url
                if url.startswith(('https://', 'http://')):
                    clean.update(target='_blank', rel='noopener noreferrer')
        if tag == 'img' and attrs.get('src'):
            url = attrs['src']
            clean['src'] = ASSET_MAP.get(url, url)
            clean['alt'] = attrs.get('alt') or '発表資料'
            clean['loading'] = 'lazy'
        if tag in ('td', 'th'):
            for name in ('colspan', 'rowspan'):
                if attrs.get(name, '').isdigit():
                    clean[name] = attrs[name]
        self.output.append('<' + tag + ''.join(f' {key}="{E(value, quote=True)}"' for key, value in clean.items()) + '>')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
            return
        if not self.skip and tag in self.tags and tag not in self.void:
            self.output.append(f'</{tag}>')

    def handle_data(self, value):
        if not self.skip:
            self.output.append(E(value))

def article_html(value):
    parser = ArticleHTML()
    parser.feed(value)
    return re.sub(r'<p>\s*</p>', '', ''.join(parser.output))

def nav(active, mobile=False):
    items = [('/#vision', '私たちのビジョン'), ('/service/', '事業紹介'), ('/news/', 'ニュース'), ('/about/', '私たちについて')]
    if mobile:
        items.append(('/contact/', 'お問い合わせ'))
    return ''.join(f'<a href="{url}"' + (' aria-current="page"' if active == url else '') + '>' + (f'<small>0{i}</small>' if mobile else '') + E(label) + '</a>' for i, (url, label) in enumerate(items, 1))

LOGO = '<img src="/assets/dxtrl-official.png" width="360" height="168" alt="DXTRL" class="official-logo">'
CTA = '''<section class="contact-cta" aria-labelledby="contact-cta-title"><div class="wrap contact-inner"><div><p class="eyebrow">LET'S MOVE FORWARD.</p><h2 id="contact-cta-title">次の一歩を、一緒に。</h2><p>ディーラーの変革から、新たなモビリティ事業まで。<br>あなたの構想を、お聞かせください。</p></div><a class="contact-action" href="/contact/"><span>お問い合わせ</span><span class="contact-circle" aria-hidden="true">↗</span></a></div></section>'''

def page(path, title, description, content, active='', cta=True, body_class=''):
    target = OUT / path.strip('/') / 'index.html' if path != '/404.html' else OUT / '404.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    head = f'''<!doctype html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#ffffff"><meta name="description" content="{E(description, quote=True)}"><title>{E(title)}</title><meta property="og:title" content="{E(title, quote=True)}"><meta property="og:description" content="{E(description, quote=True)}"><meta property="og:type" content="website"><meta property="og:locale" content="ja_JP"><link rel="icon" href="/assets/dxtrl-official.png" type="image/png"><link rel="stylesheet" href="/styles.css?v=20260911-site-visuals2"><link rel="stylesheet" href="/tech.css?v=20260911-site-visuals2"><script src="/app.js?v=20260911-site-visuals2" defer></script></head>
<body class="{body_class}"><a class="skip-link" href="#main">本文へ移動</a><header class="site-header"><a class="wordmark" href="/" aria-label="DXTRL ホーム">{LOGO}</a><nav class="desktop-nav" aria-label="メインナビゲーション">{nav(active)}</nav><a class="header-contact" href="/contact/">お問い合わせ <span aria-hidden="true">↗</span></a><button class="menu-toggle" aria-label="メニューを開く" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span></button></header><nav class="mobile-menu" id="mobile-menu" aria-label="モバイルナビゲーション" inert>{nav(active, True)}<p>DRIVING THE NEXT MOBILITY.</p></nav><main id="main">'''
    footer = f'''</main><footer class="site-footer"><div class="wrap"><div class="footer-top"><a class="wordmark" href="/" aria-label="DXTRL ホーム">{LOGO}</a><nav class="footer-links" aria-label="フッターナビゲーション">{nav(active)}<a href="/contact/">お問い合わせ</a></nav><a class="back-top" href="#top" aria-label="ページの先頭へ">↑</a></div><div class="footer-bottom"><span>DRIVING THE NEXT MOBILITY.</span><span>© 2026 DXTRL Inc.</span></div></div></footer></body></html>'''
    target.write_text(head + content + (CTA if cta else '') + footer, encoding='utf-8')

def breadcrumbs(label, parent=None):
    middle = f'<a href="{parent[0]}">{E(parent[1])}</a><span aria-hidden="true">/</span>' if parent else ''
    return f'<nav class="breadcrumbs" aria-label="現在の位置"><a href="/">HOME</a><span aria-hidden="true">/</span>{middle}<span aria-current="page">{E(label)}</span></nav>'

def page_hero(en, ja, intro=''):
    return f'<section class="page-hero" id="top"><div class="wrap">{breadcrumbs(en)}<h1 class="large-en">{en}<em>.</em></h1><p class="page-subtitle">{ja}</p>' + (f'<p class="intro">{intro}</p>' if intro else '') + '</div></section>'

def news_rows(items):
    return '<div class="news-list">' + ''.join(f'<a class="news-row" href="{a["path"]}/"><time datetime="{a["date"].replace(".", "-")}">{a["date"]}</time><span class="news-category">{E(" / ".join(a["categories"]))}</span><h3>{E(a["title"])}</h3><span class="news-arrow" aria-hidden="true">↗</span></a>' for a in items) + '</div>'

def future_films():
    films = json.loads((SRC / 'content/films.json').read_text())
    tabs, panels = [], []
    for i, film in enumerate(films):
        key = film['id']
        version = '?v=' + E(film['asset_version'], quote=True) if film.get('asset_version') else ''
        tabs.append(f'<button class="future-tab" id="future-tab-{key}" role="tab" aria-controls="future-panel-{key}" aria-selected="{str(i == 0).lower()}" tabindex="{0 if i == 0 else -1}"><span>0{i+1}</span>{E(film["tab"])}</button>')
        panels.append(f'''<article class="future-panel" id="future-panel-{key}" role="tabpanel" aria-labelledby="future-tab-{key}" tabindex="0"{'' if i == 0 else ' hidden'}><div class="film-frame"><video id="film-{key}" class="concept-video" data-src="/assets/video/{key}.mp4{version}" poster="/assets/video/{key}-poster.jpg{version}" width="1280" height="720" muted loop playsinline preload="none" aria-label="{E(film['title'], quote=True)}を描くコンセプト映像" aria-describedby="future-film-caption"></video><button class="film-control" data-film-toggle="film-{key}" aria-controls="film-{key}" aria-label="映像を再生" aria-pressed="false"><span data-film-icon aria-hidden="true">▶</span><span data-film-label>再生</span></button><p class="film-error" hidden>映像を読み込めませんでした。<button type="button" data-film-retry="film-{key}">再読み込み</button></p></div><div class="future-panel-copy"><p class="eyebrow">{E(film['label'])}</p><h3>{E(film['title'])}</h3><p>{E(film['copy'])}</p></div></article>''')
    return '<div class="future-cinema"><div class="future-tabs" role="tablist" aria-label="未来構想の映像を選ぶ" aria-orientation="horizontal">' + ''.join(tabs) + '</div><div class="future-panels">' + ''.join(panels) + '</div></div><p class="film-caption" id="future-film-caption">映像は、目指す移動・運用体験を描いたAI生成の未来構想です。</p>'

def service_visual(s):
    photos = {
        'lymo-day.webp': ('Lymoの撮影より、車のそばで会話する二人', '現場から、移動の新しい可能性へ。', 1800, 1200),
        'dealer.webp': ('自動車販売店の外観', '現場から、移動の新しい可能性へ。', 600, 300),
        'local-partner.webp': ('公園の道でCC01-Tに乗る女性。Lymo Local Partnerの実写写真', 'CC01-Tを活用した、地域の移動イメージ。', 1800, 1200),
        'dtf-ai-native.webp': ('地域の移動を支えるAIネイティブなディーラーの構想イメージ', 'AIネイティブなディーラーの構想イメージ（AI生成）', 1672, 941),
    }
    alt, caption, width, height = photos[s['photo']]
    return f'<figure class="service-visual"><img src="/assets/photos/{s["photo"]}" width="{width}" height="{height}" alt="{alt}" loading="lazy"><figcaption>{caption}</figcaption></figure>'

def service_card(s):
    if s['path'] == '/service/Lymo':
        title = '<img src="/assets/lymo-official.png" width="1006" height="332" alt="Lymo">'
    else:
        title = E(s['display_name'])
    cover = service_visual(s) if s['photo'] in ('local-partner.webp', 'dtf-ai-native.webp') else ''
    return f'<article class="service-card"><p class="eyebrow">{s["label"]}</p>{cover}<h2>{title}</h2><p>{E(s["description"])}</p><a class="text-link" href="{s["path"]}/">詳しく見る <span aria-hidden="true">↗</span></a></article>'

if __name__ == '__main__':
    # dist is reproducible output; all editable source lives under src.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / 'assets', OUT / 'assets')
    for file in ('styles.css', 'tech.css', 'app.js'):
        shutil.copy2(SRC / file, OUT / file)
    (OUT / '.nojekyll').write_text('')
    ASSET_MAP = json.loads((SRC / 'content/asset-map.json').read_text())
    articles = json.loads((SRC / 'content/articles.json').read_text())
    services = json.loads((SRC / 'content/services.json').read_text())
    names = {
        '/service/Lymo': ('Lymo', 'MOBILITY PLATFORM', '車両の可能性を、地域の可能性に。', 'lymo-day.webp'),
        '/service/lymo-series': ('Dealer AX / Dealer OS', 'DEALER INTELLIGENCE', '現場に寄り添い、変革を実装する。', 'dealer.webp'),
        '/service/dtf': ('Dealer Transformation Fund', 'HANDS-ON MANAGEMENT / 準備中', 'ディーラーの、その先をともに。', 'dtf-ai-native.webp'),
        '/service/x-iuiE4-': ('Lymo Local Partner', 'LOCAL MOBILITY / BPO', '地域に、新しい移動の選択肢を。', 'local-partner.webp')
    }
    for s in services:
        s['display_name'], s['label'], s['heading'], s['photo'] = names[s['path']]
        if s['path'] == '/service/lymo-series':
            s['title'] = 'Dealer AX / Dealer OS | 自動車ディーラー経営DX・AX'

    first = articles[0]
    ticker = f'<a class="news-ticker wrap" href="{first["path"]}/"><span class="eyebrow">LATEST NEWS</span><time datetime="{first["date"].replace(".", "-")}">{first["date"]}</time><strong>{E(first["title"])}</strong><span class="ticker-arrow" aria-hidden="true">↗</span></a>'
    home = (SRC / 'pages/home.html').read_text().replace('{{LATEST_NEWS}}', ticker).replace('{{NEWS_ROWS}}', news_rows(articles[:3])).replace('{{FUTURE_FILMS}}', future_films())
    page('/', 'DXTRL｜モビリティの未来を、動かす。', 'DXTRLは、ディーラーの現場からモビリティの未来をつくる会社です。Dealer AX、Dealer OS、Lymoを通じて、地域の移動に新しい可能性を。', home)
    page('/about/', '私たちについて｜DXTRL', 'DXTRLの使命、社名の由来、創業メンバーと会社概要。日本の運用力を、未来の社会基盤へ。', (SRC / 'pages/about.html').read_text(), active='/about/', body_class='about-page')
    page('/contact/', 'お問い合わせ｜DXTRL', 'DXTRLへのサービス導入、協業、取材などのお問い合わせ。', (SRC / 'pages/contact.html').read_text(), active='/contact/', cta=False)

    for slug, category in [('', None), ('press', 'プレスリリース'), ('notice', 'お知らせ')]:
        path = '/news/' if not slug else f'/news/category/{slug}/'
        filter_items = [('/news/', 'すべて'), ('/news/category/press/', 'プレスリリース'), ('/news/category/notice/', 'お知らせ')]
        filters = '<nav class="news-filter" aria-label="ニュースのカテゴリー">' + ''.join(f'<a href="{url}"' + (' aria-current="page"' if url == path else '') + f'>{label}</a>' for url, label in filter_items) + '</nav>'
        items = [a for a in articles if category is None or category in a['categories']]
        content = page_hero('NEWS', category or 'ニュース') + '<section class="section-pad"><div class="wrap">' + filters + news_rows(items) + '</div></section>'
        page(path, (category or 'ニュース') + '｜DXTRL', 'DXTRLの事業やLymoの展開、プレスリリース、メディア掲載をお知らせします。', content, active='/news/')

    for a in articles:
        markup = article_html(a['body_html'])
        covers = [ASSET_MAP[x] for x in a['images'] if x in ASSET_MAP and ASSET_MAP[x] not in markup]
        cover = ''.join(f'<figure class="article-cover"><img src="{url}" alt="{E(a["title"], quote=True)}の発表資料"></figure>' for url in covers)
        content = f'<article id="top" class="content-narrow"><header class="article-head">{breadcrumbs("ARTICLE", ("/news/", "NEWS"))}<div class="article-meta"><time datetime="{a["date"].replace(".", "-")}">{a["date"]}</time><span>{E(" / ".join(a["categories"]))}</span></div><h1>{E(a["title"])}</h1></header><div class="article-body">{cover}{markup}</div><div class="article-bottom"><a class="text-link" href="/news/">ニュース一覧へ <span aria-hidden="true">↗</span></a></div></article>'
        page(a['path'] + '/', a['title'] + '｜DXTRL', re.sub(r'\s+', '', a['body_text'])[:130], content, active='/news/')

    corporate_cards = '''<article class="service-card"><p class="eyebrow">01 / FIELD INTELLIGENCE</p><figure class="business-illustration"><img src="/assets/illustrations/dealer-ax.webp" width="1672" height="941" alt="ディーラーの担当者と実装パートナーが、タブレットを囲んで現場の業務改善に取り組むイラスト" loading="lazy"></figure><h2>Dealer AX</h2><p>業務設計、AI活用、実装・運用を一体で支援。現場の変革を、お客様と向き合う時間へつなげます。</p><a class="text-link" href="/service/lymo-series/#dealer-ax">詳しく見る <span aria-hidden="true">↗</span></a></article><article class="service-card"><p class="eyebrow">02 / OPERATING SYSTEM</p><figure class="business-illustration"><img src="/assets/illustrations/dealer-os.webp" width="1672" height="941" alt="顧客対応・車両・整備・事務の現場を、共通の基盤でつなぐDealer OSのイラスト" loading="lazy"></figure><h2>Dealer OS</h2><p>顧客・車両・店舗と業務ルールを共通のモデルへ。現場の理解、判断、実行を支える基盤を構築します。</p><a class="text-link" href="/service/lymo-series/#dealer-os">構想を見る <span aria-hidden="true">↗</span></a></article>'''
    service_content = page_hero('BUSINESS', '事業紹介', 'Dealer AXで現場を変え、Dealer OSで知見を基盤に。Lymoで地域の移動へつなぎます。') + '<section class="section-pad"><div class="wrap"><div class="service-grid core-service-grid">' + corporate_cards + service_card(services[0]) + '</div><div class="service-grid supporting-services">' + ''.join(service_card(s) for s in services[2:]) + '</div></div></section>'
    page('/service/', '事業紹介｜DXTRL', 'Dealer AX、Dealer OS、Lymo。現場の変革から、モビリティの社会インフラへ。', service_content, active='/service/')
    for s in services:
        hero = f'<section class="page-hero" id="top"><div class="wrap">{breadcrumbs("SERVICE", ("/service/", "BUSINESS"))}<p class="eyebrow">{s["label"]}</p><h1>{E(s["display_name"])}</h1><p class="intro">{E(s["title"].split("|", 1)[-1].strip())}</p></div></section>'
        external = ''
        if s['external_url']:
            external = f'<a class="button secondary" href="{s["external_url"]}" target="_blank" rel="noopener noreferrer">公式サービスサイトへ <span aria-hidden="true">↗</span></a>'
        if s['photo']:
            photo = service_visual(s)
        else:
            note = ('本事業は準備中です。提供内容についてはお問い合わせください。' if s['path'].endswith('dtf') else '特定小型原付などのシェアリングを、地域のモビリティ事業者とともに。導入・運用に関するご相談を承ります。')
            photo = f'<aside class="service-info"><p class="eyebrow">{s["label"]}</p><h3>地域のパートナーと、<br>次の一歩へ。</h3><p>{note}</p><a class="text-link" href="/contact/">事業について相談する <span aria-hidden="true">↗</span></a></aside>'
        related = '<div class="related-services"><h2>ほかの事業を見る</h2><nav aria-label="関連する事業">' + ''.join(f'<a href="{x["path"]}/">{E(x["display_name"])} ↗</a>' for x in services if x != s) + '</nav></div>'
        platform_details = ''
        if s['path'] == '/service/lymo-series':
            platform_details = '''<div class="service-platform-grid"><section id="dealer-ax"><p class="eyebrow">01 / FIELD INTELLIGENCE</p><h2>Dealer AX</h2><h3>AIを、現場の力に。</h3><figure class="business-illustration"><img src="/assets/illustrations/dealer-ax.webp" width="1672" height="941" alt="ディーラーの担当者と実装パートナーが、タブレットを囲んで現場の業務改善に取り組むイラスト" loading="lazy"></figure><p>日々の業務を知るところから、変革は始まる。業務設計、AI活用、実装・運用を一体で支援し、お客様と向き合う時間を生み出します。</p><div class="tags"><span>業務設計</span><span>AI実装</span><span>運用支援</span></div><a class="text-link" href="/contact/">Dealer AXについて相談する <span aria-hidden="true">↗</span></a></section><section id="dealer-os"><p class="eyebrow">02 / OPERATING SYSTEM</p><h2>Dealer OS</h2><h3>現場のつながりを、共通の基盤へ。</h3><figure class="business-illustration"><img src="/assets/illustrations/dealer-os.webp" width="1672" height="941" alt="顧客対応・車両・整備・事務の現場を、共通の基盤でつなぐDealer OSのイラスト" loading="lazy"></figure><p>顧客・車両・店舗の関係と、「点検中の車は貸し出せない」といった業務ルールを整理した「現場の共通地図」がOntology（オントロジー）です。人とAIが同じ前提で判断し、店舗で得た知見をほかの店舗でも使える仕組みに育てるため、Dealer OSの土台にします。</p><div class="tags"><span>業務モデル</span><span>判断・実行</span><span>共通プロダクト</span></div><a class="text-link" href="/#ontology">業務モデルの構想を見る <span aria-hidden="true">↗</span></a></section></div>'''
        content = hero + f'<section class="section-pad"><div class="wrap"><div class="service-detail"><div><h2>{s["heading"]}</h2><p>{E(s["description"])}</p>{external}</div>{photo}</div>{platform_details}{related}</div></section>'
        page(s['path'] + '/', s['title'] + '｜DXTRL', s['description'], content, active='/service/')

    page('/404.html', 'ページが見つかりません｜DXTRL', 'お探しのページは見つかりませんでした。', '<section class="not-found wrap" id="top"><p class="eyebrow">PAGE NOT FOUND</p><h1>404<em>.</em></h1><h2>お探しのページが見つかりません。</h2><p>URLをご確認いただくか、トップページからご覧ください。</p><a class="button" href="/">トップページへ <span aria-hidden="true">↗</span></a></section>', cta=False)
    print(f'Built {len(list(OUT.rglob("*.html")))} pages, including {len(articles)} complete news articles.')
