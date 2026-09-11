# DXTRL corporate website

2026年9月10日のレビューと追加指示を反映したDXTRL企業サイトです。

## 変更内容

白・ライトグレーの明るい面、深いグリーン、ライムのアクセントで、DXTRLの先端テック感を表現。冒頭と事業紹介でDealer AX・Dealer OS・Lymoを同じ重みで扱います。制作済みの6本のコンセプト映像とキービジュアルを再利用し、Lymoの現在のサービスには実写写真を使用。公式Lymoロゴは原本のままです。

About Us、全12ニュース記事、2カテゴリー、4サービス、事業一覧、お問い合わせ、404を含む24ページを収録。企業サイト内のリンクは同じサイト内で完結します。Lymo本体、提携先、掲載媒体への外部リンクは公式導線として保持しています。

お問い合わせはdealer.lymo.lifeが案内するDXTRL既存Googleフォームを埋め込み、別タブで開くリンクと公式電話を併記。Studio APIへの送信依存はありません。

## 更新する場所

| 内容 | ソース |
| --- | --- |
| トップ・About・お問い合わせ | src/pages/ |
| ニュース本文・日付・カテゴリー | src/content/articles.json |
| サービス本文 | src/content/services.json |
| 共通の基本レイアウト / DXTRLのデザイン | src/styles.css / src/tech.css |
| 未来構想の映像・説明 | src/content/films.json / src/assets/video/ |
| メニュー・事業タブ・未来構想タブ・動画再生 | src/app.js |
| 共通テンプレート・詳細ページ生成 | scripts/build_site.py |
| 写真・ロゴ・記事画像 | src/assets/ |
| 素材出典 | asset-provenance.json |

Python 3とNode.jsで生成・静的検証できます。外部パッケージのインストールは不要です。

```sh
python3 scripts/build_site.py
python3 scripts/validate_site.py
node --check dist/app.js
```

`dist/`は生成物です。ソースを変更して再生成し、ソースとdistの両方をコミットしてください。トップの最新3件・ニュース一覧・各記事は同じJSONから更新されます。

## GitHub運用

`.github/workflows/site.yml`はPR時に生成・内部リンク検証・JavaScript構文検証を行い、mainへの反映時にGitHub Pagesへ公開します。専用リポジトリのSettings → Pages → SourceをGitHub Actionsに設定して利用してください。

`scripts/prepare_pages.py`がGitHub Pagesのベースパスに合わせて公開用コピーを作るため、プロジェクトURLと独自ドメインのどちらでも内部リンクを維持します。Sitesへ配信するdistは変更しません。GitHubの秘密情報をソースへ保存する必要はありません。

設定根拠: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

接続済みGitHubでは、DXTRL-team/lymo-lpはdealer.lymo.lifeを配信する既存のLymo用LPでした。企業サイト用のリポジトリは確認できず、既存LPへの書き込みはしていません。企業サイト専用のリポジトリが必要です。

## 公開状況・Studio移行

この更新は既存の確認用Sites URLへの反映です。dxtrl.comのDNS・Studio契約は変更していません。`.openai/hosting.json`の既存プロジェクト紐付けを保持してください。

お問い合わせは既存Googleフォームが受け付けます。公開フォームと必須項目は確認済みですが、テスト送信・受信確認は行っていません。本番切替時はdxtrl.comの配信先・HTTPS・既存パス・フォーム受信を確認してからStudioを解約してください。

Lymoの別サイト（about.lymo.life / dealer.lymo.life）は、この企業サイト移行の対象外です。元のprivacy・recruitページは404でサイトマップにも存在しませんでした。架空のページや個人情報保護方針は追加していません。

## 検証

24ページの内部リンク・フラグメント・ローカル画像・見出し・ARIA・画像alt・iframeタイトル・12記事の収録、JavaScript構文、GitHub Pagesベースパス変換を確認。Lymo公式ロゴのSHA-256一致も確認。ブラウザーの表示・操作テストは未実施です。

## 映像の扱い

6本は既存素材を無加工で再利用しています。ヒーロー1本と、未来構想タブ5本（運用拠点、ロボット清掃、整備、自動運転、マイクロモビリティ）。About Usにも既存の拠点キービジュアルを使用し、生成素材には未来構想の明示を付けています。

動画は表示中かつ選択中のものだけ読み込み・再生し、画面外、非選択タブ、別ブラウザータブ、メニュー展開時は停止します。個別再生・一時停止、読み込みエラーの再試行、動きを減らす設定、データ節約設定に対応。動画とポスターの原本一致を確認しています。再生状態は、選択タブ切替・手動停止の保持・背景タブ停止／復帰・再試行・動きを減らす設定をシミュレーションして検証しています。出典はvideo-provenance.jsonに記録しています。
