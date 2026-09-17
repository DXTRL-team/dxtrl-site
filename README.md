# DXTRL コーポレートサイト

[dxtrl.com](https://dxtrl.com) のソース。静的サイト（Python でHTML生成）+ Vercel serverless function（Node.js、お問い合わせ受付）で構成。

## ホスティング構成

| レイヤー | 使ってる仕組み |
| --- | --- |
| ソース管理 | GitHub: [DXTRL-team/dxtrl-site](https://github.com/DXTRL-team/dxtrl-site) |
| デプロイ | [Vercel](https://vercel.com/dxtrl/dxtrl-site) — mainへpushで自動デプロイ |
| メール送信 | [Resend](https://resend.com/domains) — `noreply@dxtrl.com` から送信 |
| Slack通知 | Slack Incoming Webhook（DXTRL Contact Notifier App） |
| DNS | Squarespace（ドメイン管理）※お名前.comは使っていない |

`main` にコミットが積まれると Vercel が自動でビルド → `dxtrl.com` / `www.dxtrl.com` に反映されます。作業ブランチや PR を作った場合はプレビュー URL が自動生成されます。

`dist/` は Vercel が自動生成するので、リポには含めていません（`.gitignore` 対象）。ソース（`src/` `api/` `scripts/`）だけ編集すれば OK です。

## はじめての方へ（コマンド不要）

ローカルに何もセットアップしなくても、**GitHub の Web 画面だけで編集 → 自動で本番反映**まで完結できます。プログラミングに慣れていない方はこの流れでどうぞ。

1. https://github.com/DXTRL-team/dxtrl-site を開いてログイン
2. 変更したいファイルをクリック（例：ニュース追加なら `src/content/articles.json`）
3. 右上の**鉛筆アイコン** ✏️ をクリック → 直接編集できるモードになる
4. 変更後、下にある「**Commit changes**」ボタンで内容を保存
   - コミット先を「Commit directly to main」にすると本番反映
   - 「Create a new branch」→「Propose changes」にするとプレビューURLが作られる（**大きな変更のときはこちら推奨**）
5. Vercel が1〜2分でビルド → dxtrl.com / プレビュー URL に反映

### ChatGPT / Claude と組み合わせるコツ

コードや HTML に慣れていなくても、ChatGPTに「今のファイル」と「やりたいこと」を伝えれば書き換えてくれます。テンプレートは以下：

```
DXTRLコーポレートサイト（https://github.com/DXTRL-team/dxtrl-site）の
「◯◯」を変更したいです。

対象ファイル: src/pages/home.html
現在の中身は以下の通り：

（GitHubで開いた対象ファイルを丸ごとコピー＆ペースト）

やりたい変更：
・ヒーローの見出しを「地域の移動を、次のインフラへ。」に変えたい
・「未来のインフラへ。」の「未来」の色をそのまま緑のままにしてほしい

変更後の完全なファイル内容を出してください。
```

ポイント:

- **必ず「対象ファイル名」を伝える**：`src/pages/home.html` のように相対パスで
- **今の中身を丸ごと貼る**：AIは推測で書きがちなので、元ソースを見せると精度が上がる
- **HTMLの一部だけ変更したいときは、変更後の完全なファイル内容をもらう**（部分だけだと GitHub に貼り直しづらい）
- **記事追加のとき（`src/content/articles.json`）は「JSON配列の先頭に新しい記事を1件追加してください」と伝える**。既存記事を壊さないように「他の記事は変更しない」と念押しすると安全
- **AIの出力を貼り付けたら、変更後のプレビューURLで見た目確認 → 問題なければmainにマージ** の流れが安全

### ローカルで再現したい方へ

「本番に反映する前に、自分のパソコンでプレビューして見た目を確認したい」場合の手順です。ターミナルを1回だけ触れれば OK。

**必要なもの**（初回セットアップだけ）:

1. **GitHub Desktop** をインストール：https://desktop.github.com/
   - Macなら .dmg をダウンロードして Applications に入れる
   - 起動時に GitHub アカウントでサインイン
2. **Python 3** を確認：ターミナル（Macなら Applications → Utilities → Terminal）で `python3 --version` を実行
   - 何かバージョンが出たらOK。「command not found」なら https://www.python.org/downloads/ からインストール

**リポジトリを手元に持ってくる**:

1. GitHub Desktop を開く
2. 「File」→「Clone Repository」→「URL」タブ
3. `DXTRL-team/dxtrl-site` を選択（またはURL `https://github.com/DXTRL-team/dxtrl-site` を貼る）
4. Local path を選ぶ（例：`~/Documents/dxtrl-site`）→「Clone」

**プレビューを開く**（毎回の作業）:

1. GitHub Desktop で「Repository」→「Open in Terminal」でターミナルが開く
2. 以下2行を実行

   ```sh
   python3 scripts/build_site.py
   python3 -m http.server -d dist 8000
   ```

3. ブラウザで http://localhost:8000 を開く → 本番と同じ見た目が出る
4. ソース（`src/` の中）を編集したら **1つ目のコマンドをもう一度実行**（build_site.py）→ ブラウザをリロード
5. 確認できたら、GitHub Desktop で「Commit to main」または新ブランチにpush

**ターミナル終了方法**: `Ctrl+C` でサーバー停止 → ウィンドウを閉じる

**ChatGPT/Claudeに聞くとき**：エラーが出たらエラーメッセージ全文を貼って「これはどういう意味？どうしたらいい？」と聞けば教えてくれます。macOS/Windowsどちらか、Python のバージョンも一緒に伝えると精度上がります。

**お問い合わせフォームの動作テストは、ローカルではできません**（Vercel serverless function は本番/プレビュー環境でしか動きません）。フォーム挙動を試したいときはブランチにpushして Vercel の Preview URL で確認してください。

### やってはいけないこと

- `.github/`, `scripts/`, `api/`, `package.json`, `vercel.json` は仕組みの中枢。AIに勧められても、内容が理解できないうちは触らない
- `src/assets/` の中の画像/動画ファイルを差し替えたい場合、**同じファイル名で上書き**すること（別名にすると参照が切れる）
- Slack Webhook URL / Resend API キー / Vercel トークン等の秘密情報は、**GitHub のファイル・PR・Issue にも絶対に貼らない**
- `dist/` フォルダは自動生成されるので、間違って PR に含まれていたら削除してから commit

## 記事を追加・編集する（一番よくやる作業）

すべて `src/content/articles.json` の1配列に入っています。**配列の先頭に近いほど新しい記事として扱われる**（トップページの最新3件はここの先頭3件）。

新しい記事を追加するときの最小フィールド:

```jsonc
{
  "url": "https://dxtrl.com/news/20260915",   // 参考、なくてもよい
  "path": "/news/20260915",                    // 記事のURL（半角英数記号のみ）
  "title": "記事タイトル",
  "date": "2026.09.15",                        // 表示日
  "categories": ["お知らせ"],                  // 「お知らせ」または「プレスリリース」
  "body_html": "<p>本文HTML。段落 <strong>装飾</strong> リンク...</p>",
  "body_text": "本文プレーンテキスト（メタ description に使われる）",
  "images": []                                  // 記事内画像のURL（任意）
}
```

`path` はスラッシュ始まりで、他の記事と重複しないユニークな文字列にする（例：日付ベースの `/news/20261015`）。

編集後の流れ:

```sh
python3 scripts/build_site.py       # dist/ を再生成
python3 scripts/validate_site.py    # リンク切れ・ARIA・画像 alt 等のチェック
git add src/content/articles.json
git commit -m "Add news: XXX"
git push
```

`dist/` は生成物で、Git管理の対象外です。ソースだけをコミットし、Vercelのビルドで生成します。

## そのほかの編集場所

| 内容 | ファイル |
| --- | --- |
| トップページの本文 | `src/pages/home.html` |
| About Us（会社紹介・メンバー） | `src/pages/about.html` |
| お問い合わせページ本文 | `src/pages/contact.html` |
| サービス（Dealer AX / Dealer OS / Lymo / DTF / LLP）の説明 | `src/content/services.json` |
| 未来構想（動画タブ）の見出し・キャッチ | `src/content/films.json` |
| デザイン（色・タイポグラフィ・共通レイアウト） | `src/styles.css`, `src/tech.css` |
| ヘッダー・フッターナビの共通テンプレート | `scripts/build_site.py`（`nav()` と `page()`） |
| 動画/画像素材 | `src/assets/` 配下 |

`src/` を編集 → `scripts/build_site.py` を実行 → `dist/` が更新される、というワンステップ構成です。`scripts/build_site.py` は共通レイアウト・記事詳細ページ・ニュース一覧を1回で生成します。

## 本文（コピー）を変える

各ページは `src/pages/*.html` にプレーンなHTMLで入っています。`<h1>` や `<p>` の中身を書き換えるだけで反映されます。

```html
<!-- src/pages/home.html の一部 -->
<section class="hero">
  <p class="eyebrow">DEALERSHIP × DIGITAL × DECENTRALIZED</p>
  <h1>日本のディーラーを、<br><span>未来のインフラへ。</span></h1>
  <p class="hero-description">
    現場の知を、テクノロジーでつなぐ。<br>
    Dealer AX、Dealer OS、Lymoを通じて、<br>
    次のモビリティインフラをつくる。
  </p>
  ...
```

**書き方の目安**:

- 装飾は既存のクラス名を再利用する（`eyebrow` は緑の小さいラベル、`section-pad` は上下の余白、`text-link` は矢印つきリンクなど）。新しいクラスを増やすより既存パターンを使うと統一感が保てます。
- `<em>` タグは緑のアクセント文字になります（CSSで `color: var(--green)`）。強調したい単語に使えます。
- 改行は `<br>` を明示。文章のリズムに関わるので、改行位置は視覚的に確認してください。
- サービス紹介の文言は HTMLではなく `src/content/services.json` の中の `description` `title` を編集します。

## デザインを変える

デザインの基本は `src/styles.css` の先頭で定義したCSSカスタムプロパティ（デザイントークン）で決まっています。まずここを触ると、サイト全体を安全に変更できます。

```css
:root {
  --ink: #16211d;         /* 本文の文字色 */
  --green: #286344;       /* メインアクセント（em、eyebrow、リンク hover 等） */
  --mint: #eef2f0;        /* 淡いグリーン背景（Vision statement など） */
  --cream: #f5f6f6;       /* オフホワイト背景（Lymo Story、Company セクション） */
  --muted: #56625b;       /* 補助文字色 */
  --line: #d4ddd7;        /* 境界線 */
  --accent: #caf57c;      /* ライムアクセント（現在未使用のスペア） */
  --dark: #14211b;        /* ダーク面 */
  --wrap: 1280px;         /* コンテンツ最大幅 */
  --gutter: clamp(22px, 5vw, 80px);  /* 左右の余白 */
}
```

たとえば「もっと濃いグリーンに寄せたい」なら `--green` を `#1e5236` に変える → サイト全体でボタン・アクセント・リンクhoverの色が一括で変わります。

**よくある変更ポイント**:

| やりたいこと | 触るファイル・場所 |
| --- | --- |
| ブランドカラーを変える | `:root` の `--green` `--mint` `--accent` |
| コンテンツ幅を広げる | `:root` の `--wrap`（現在 1280px） |
| 左右の余白を調整 | `:root` の `--gutter` |
| フォントを変える | `:root` の `font-family:` |
| 見出しの大きさ | `h1{...} h2{...} h3{...}`（レスポンシブに `clamp(...)` で書いてある） |
| ボタンの見た目 | `.button` `.button.secondary` |
| ヘッダーの高さ・レイアウト | `.site-header` `.desktop-nav` |
| セクションごとの見た目 | 各セクションのクラス（`.hero`, `.vision-statement`, `.business-panel`, `.future` 等） |
| モバイル表示の調整 | `@media(max-width:1100px)` `@media(max-width:820px)` `@media(max-width:600px)` |

`src/styles.css` は共通のデザイン、`src/tech.css` は Vision Film / Service ページのテック寄り演出（グラデーション、動画枠など）を持っています。全体の色味を変えるなら `styles.css` の `:root` だけで済むケースが多いです。

`src/styles.css` は改行が少ない圧縮風の書き方になっていますが、普通のCSSなので改行しても動作は変わりません。読みやすく整形して編集する→そのままコミットで問題ありません。

## ローカルで確認する（プレビュー）

デザインや文言を変えるときは、pushする前に見た目を確認するのがおすすめです。

```sh
# 1. ソースを編集（src/ の中）

# 2. dist/ を再生成
python3 scripts/build_site.py

# 3. 静的サーバで開く
python3 -m http.server -d dist 8000
# → http://localhost:8000 をブラウザで開く

# 4. 問題なければ検証してからコミット
python3 scripts/validate_site.py
node --check dist/app.js
git add src
git commit -m "..."
git push
```

Vercel のプレビュー機能を使う場合は、`main` ではなく作業ブランチにpush → GitHub上でPR作成すれば、そのPRにプレビューURL（`dxtrl-site-<hash>-dxtrl.vercel.app`）がコメントされます。デザインの相談・レビューはPR上でやると楽です。

## お問い合わせフォーム（送信の仕組み）

- フロント: `src/pages/contact.html` の HTML フォーム + `src/app.js` の送信処理
- バックエンド: `api/contact.js`（Vercel Node.js serverless function）
- フィールド: お名前 / メール / 会社名 / 電話 / 内容（すべて必須）+ 非表示 honeypot
- 送信フロー:
  1. ブラウザから `POST /api/contact` に JSON で送る
  2. `api/contact.js` がバリデーション
  3. Resend で `tetsuro_ikenishi@dxtrl.com` にメール送信（`CONTACT_TO_EMAIL` で切替可能）
  4. Slack Incoming Webhook に Block Kit で通知（`SLACK_WEBHOOK_URL`）
  5. ブラウザには `{ok: true}` を返して、フォームを成功カードに置き換え

環境変数は Vercel の [プロジェクト Environment Variables](https://vercel.com/dxtrl/dxtrl-site/settings/environment-variables) で管理:

| 変数名 | 用途 |
| --- | --- |
| `RESEND_API_KEY` | Resend API キー（Secret） |
| `CONTACT_TO_EMAIL` | 受信先メールアドレス（カンマ区切りで複数可） |
| `CONTACT_FROM_EMAIL` | 送信元。現状 `DXTRL Website <noreply@dxtrl.com>` |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL |

環境変数を変えたら **Redeploy 必須**（Vercel の Deployments → 該当行の「⋯」→ Redeploy）。

## ローカルで確認したいとき

外部パッケージのインストールは不要です（サーバー関数以外は標準ライブラリのみで動きます）。

```sh
python3 scripts/build_site.py
python3 scripts/validate_site.py
node --check dist/app.js
node --check api/contact.js
```

生成された `dist/` を任意の静的サーバでプレビューしてください（例：`python3 -m http.server -d dist 8000`）。

serverless function をローカルで動かしたい場合は Vercel CLI:

```sh
npm i -g vercel
vercel link       # 初回のみ
vercel env pull   # ローカル .env を取得
vercel dev
```

## CI

`.github/workflows/site.yml` が PR とpush時に:
- `python3 scripts/build_site.py` を実行
- `python3 scripts/validate_site.py` でリンク・ARIA・画像 alt 等をチェック
- `node --check dist/app.js` と `node --check api/contact.js` で構文チェック

CIが落ちた場合は、生成・静的検証・構文チェックの出力を確認してください。`dist/` のコミットは不要です。

## 動画の扱い

7本のコンセプト映像は `src/assets/video/` 配下。表示中かつ選択中のときだけ読み込み・再生します（画面外/非選択タブ/バックグラウンド時は停止）。動きを減らす設定・データ節約設定にも対応済み。素材の出典は `video-provenance.json` に、その他画像は `asset-provenance.json` に記録しています。マイクロモビリティ映像を差し替える場合は、`src/content/films.json` の `asset_version` も更新すると、ブラウザーに残る古い素材を避けられます。

## トラブルシューティング

- **フォーム送信後 5xx が返る** → Vercel の [Function Logs](https://vercel.com/dxtrl/dxtrl-site/logs) を Route `/api/contact/` で絞って確認。だいたい Resend か Slack の設定変更が原因。
- **メールが届かない** → Resend の [Emails 画面](https://resend.com/emails) で送信ログを確認。DKIM/SPF は Squarespace の DNS に `resend._domainkey` `rsend` `send` `_dmarc` の4件が入っているのを保つ。
- **サイトがビルド失敗する** → `python3 scripts/build_site.py` をローカルで走らせるとエラー行が出る。だいたい `articles.json` の JSON 構文ミス（末尾カンマ、閉じ忘れ）。
- **dxtrl.com が古いサイトに戻った** → Squarespace の DNS で誰かがドメイン転送ルールを再登録した可能性。カスタムレコードの A `@` `76.76.21.21` と CNAME `www` `cname.vercel-dns.com` を確認。

## 触ってはいけない DNS レコード

Squarespace の DNS カスタムレコードのうち、以下は **絶対に消したり値を変えたりしないでください**（Gmail や Resend のメール送信が止まります）:

- TXT `@` `v=spf1 include:_spf.google.com ~all`（Google Workspace の SPF）
- TXT `google._domainkey ...`（Gmail の DKIM）
- TXT `@` `google-site-verification=...`（Google 所有権検証）
- TXT `resend._domainkey ...`（Resend の DKIM）
- CNAME `rsend`, CNAME `send`（Resend の送信経路）
- TXT `_dmarc` `v=DMARC1; p=none;`（DMARC）

## Google Analytics 4

DXTRLの既存プロパティ `504464272`（アカウント `367856898`）、ウェブストリーム `Corp`（`12141478717`）を使用します。測定IDは `src/content/analytics.json` の `G-7QT1FYYLQF` です。このIDは公開用タグの識別子で、秘密情報ではありません。

- 共通のHTML生成処理から全ページに `analytics.js` を1回だけ読み込みます。
- `https://dxtrl.com` と `https://www.dxtrl.com` だけで計測します。Vercelプレビューやlocalhostは対象外です。
- `config` の標準ページビューを使用し、手動の `page_view` は追加しません。GA4の「拡張計測機能」はOFFにしてください（履歴変更による重複やフォーム自動計測を防ぐため）。
- URLは生成時に確定したページURLを使い、クエリ・ハッシュを除外します。参照元はドメインまでとし、UTMキャンペーン別の計測はこの構成には含めません。
- 問い合わせフォームの入力値、user_id、広告向けのGoogleシグナルは送信しません。
- 計測を止める場合は `measurement_id` を `null` にして再デプロイします。

[Analyticsホーム](https://analytics.google.com/analytics/web/#/a367856898p504464272/reports/intelligenthome) のリアルタイムレポートで受信を確認できます。利用目的と停止方法はサイトの `/access-analysis/` に掲載しています。
