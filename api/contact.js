import { Resend } from 'resend';

const FIELDS = ['name', 'email', 'company', 'phone', 'message'];
const LABELS = { name: 'お名前', email: 'メールアドレス', company: '会社名', phone: 'お電話番号', message: 'お問い合わせ内容' };
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const LIMITS = { name: 120, email: 200, company: 200, phone: 30, message: 4000 };

function sanitize(value, max) {
  if (typeof value !== 'string') return '';
  let out = '';
  const normalized = value.split('\r\n').join('\n');
  for (const ch of normalized) {
    const code = ch.charCodeAt(0);
    if (code < 32 && code !== 10) continue;
    if (code === 127) continue;
    out += ch;
  }
  return out.trim().slice(0, max);
}

function escapeHtml(value) {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const body = typeof req.body === 'object' && req.body ? req.body : {};

  if (typeof body.company_url === 'string' && body.company_url.trim() !== '') {
    return res.status(200).json({ ok: true });
  }

  const data = Object.fromEntries(FIELDS.map(key => [key, sanitize(body[key], LIMITS[key])]));

  const missing = FIELDS.filter(key => !data[key]);
  if (missing.length) {
    return res.status(400).json({ error: `${missing.map(k => LABELS[k]).join('、')} を入力してください。` });
  }
  if (!EMAIL_RE.test(data.email)) {
    return res.status(400).json({ error: 'メールアドレスの形式を確認してください。' });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error('RESEND_API_KEY is not set');
    return res.status(500).json({ error: 'サーバー設定が完了していません。' });
  }
  const to = (process.env.CONTACT_TO_EMAIL || '').split(',').map(s => s.trim()).filter(Boolean);
  if (!to.length) {
    console.error('CONTACT_TO_EMAIL is not set');
    return res.status(500).json({ error: 'サーバー設定が完了していません。' });
  }
  const from = process.env.CONTACT_FROM_EMAIL || 'DXTRL Website <noreply@dxtrl.com>';

  const lines = FIELDS.map(key => `${LABELS[key]}: ${data[key]}`).join('\n');
  const subject = `[DXTRL お問い合わせ] ${data.name} 様 / ${data.company}`;
  const text = `DXTRLコーポレートサイトのお問い合わせフォームより受信しました。\n\n${lines}\n\n---\n返信は上記メールアドレスへ直接お送りください。`;
  const rows = FIELDS.map(key => `<tr><th align="left" style="padding:8px 16px 8px 0;color:#56625b;font-weight:600;white-space:nowrap;vertical-align:top">${LABELS[key]}</th><td style="padding:8px 0;white-space:pre-wrap">${escapeHtml(data[key])}</td></tr>`).join('');
  const html = `<div style="font-family:'Noto Sans JP',sans-serif;color:#16211d;line-height:1.7"><p>DXTRLコーポレートサイトのお問い合わせフォームより受信しました。</p><table cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-top:16px">${rows}</table><p style="margin-top:24px;color:#56625b;font-size:12px">返信は上記メールアドレスへ直接お送りください。</p></div>`;

  const resend = new Resend(apiKey);
  const { data: sent, error: emailError } = await resend.emails.send({
    from,
    to,
    replyTo: data.email,
    subject,
    text,
    html
  });
  if (emailError) {
    console.error('Resend error', emailError);
    return res.status(502).json({ error: '送信に失敗しました。時間を置いて再度お試しください。' });
  }

  const slackUrl = process.env.SLACK_WEBHOOK_URL;
  if (slackUrl) {
    try {
      const summary = `${data.name} 様 (${data.company}) より新規お問い合わせ`;
      const blocks = [
        {
          type: 'header',
          text: { type: 'plain_text', text: ':mailbox_with_mail: DXTRLコーポレートサイトに新規お問い合わせ', emoji: true }
        },
        {
          type: 'section',
          fields: [
            { type: 'mrkdwn', text: `*お名前*\n${data.name}` },
            { type: 'mrkdwn', text: `*会社名*\n${data.company}` },
            { type: 'mrkdwn', text: `*メールアドレス*\n<mailto:${data.email}|${data.email}>` },
            { type: 'mrkdwn', text: `*お電話番号*\n${data.phone}` }
          ]
        },
        {
          type: 'section',
          text: { type: 'mrkdwn', text: `*お問い合わせ内容*\n${data.message}` }
        },
        {
          type: 'context',
          elements: [
            { type: 'mrkdwn', text: `:clock3: ${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })} ｜ Resend ID: \`${sent?.id || 'n/a'}\`` }
          ]
        }
      ];
      const slackResponse = await fetch(slackUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: summary, blocks })
      });
      if (!slackResponse.ok) console.error('Slack webhook non-2xx', slackResponse.status, await slackResponse.text().catch(() => ''));
    } catch (slackErr) {
      console.error('Slack webhook error', slackErr);
    }
  }

  return res.status(200).json({ ok: true, id: sent?.id || null });
}
