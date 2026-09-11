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
git add src/content/articles.json dist
git commit -m "Add news: XXX"
git push
```

**dist/ もコミットに含めてください**（Vercelの build step でも作られますが、リポの中でも常に最新を保つルール）。

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

## お問い合わせフォーム（送信の仕組み）

- フロント: `src/pages/contact.html` の HTML フォーム + `src/app.js` の送信処理
- バックエンド: `api/contact.js`（Vercel Node.js serverless function）
- フィールド: お名前 / メール / 会社名 / 電話 / 内容（すべて必須）+ 非表示 honeypot
- 送信フロー:
  1. ブラウザから `POST /api/contact` に JSON で送る
  2. `api/contact.js` がバリデーション
  3. Resend で `tetsuro.ikenishi@ta-ne.co.jp` にメール送信（`CONTACT_TO_EMAIL` で切替可能）
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
- `git diff --exit-code -- dist` で「ソースを編集したのに dist を更新し忘れていないか」を検出

CI が落ちるときはたいてい最後の「dist の再生成忘れ」なので、ローカルで `python3 scripts/build_site.py` して再コミットしてください。

## 動画の扱い

6本のコンセプト映像は `src/assets/video/` 配下。表示中かつ選択中のときだけ読み込み・再生します（画面外/非選択タブ/バックグラウンド時は停止）。動きを減らす設定・データ節約設定にも対応済み。素材の出典は `video-provenance.json` に、その他画像は `asset-provenance.json` に記録しています。

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
