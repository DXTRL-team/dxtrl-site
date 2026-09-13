(() => {
  'use strict';

  const productionOrigins = new Set(['https://dxtrl.com', 'https://www.dxtrl.com']);
  const settings = document.currentScript?.dataset;
  const measurementId = settings?.measurementId || '';
  if (!productionOrigins.has(window.location.origin) ||
      !/^G-[A-Z0-9]{10}$/.test(measurementId) || window.__dxtrlGA4Loaded) return;

  // Use the fixed, generated page URL, never visitor-supplied query or hash values.
  let page;
  try {
    page = new URL(settings.pageLocation);
  } catch { return; }
  if (!productionOrigins.has(page.origin) || page.username || page.password) return;

  let referrer = '';
  try {
    const source = new URL(document.referrer);
    if (source.protocol === 'https:' || source.protocol === 'http:') referrer = source.origin;
  } catch { /* A direct visit has no referrer. */ }

  if (window.dataLayer && !Array.isArray(window.dataLayer)) return;
  window.dataLayer = window.dataLayer || [];
  if (window.gtag && typeof window.gtag !== 'function') return;
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.__dxtrlGA4Loaded = measurementId;

  window.gtag('js', new Date());
  // Enhanced measurement is disabled in GA4. This config sends the only page_view.
  window.gtag('config', measurementId, {
    page_location: page.origin + page.pathname,
    page_referrer: referrer,
    page_title: document.title,
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });

  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
  document.head.append(script);
})();
