(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.getElementById('mobile-menu');
  const main = document.getElementById('main');
  const footer = document.querySelector('.site-footer');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const videos = [...document.querySelectorAll('.concept-video')];
  const states = new Map(videos.map(video => [video, {
    visible: false, userPaused: false, userStarted: false,
    pending: false, blocked: false, failed: false
  }]));
  const saveData = Boolean(navigator.connection?.saveData);

  function canPlay(video) {
    const state = states.get(video);
    return state.visible && !state.userPaused && !state.failed && !state.blocked &&
      !document.hidden && !document.body.classList.contains('menu-open') &&
      !video.closest('[hidden]') && (!(reducedMotion.matches || saveData) || state.userStarted);
  }
  function updateControl(video) {
    const button = document.querySelector(`[data-film-toggle="${video.id}"]`);
    if (!button) return;
    const playing = !video.paused;
    button.setAttribute('aria-pressed', String(playing));
    button.setAttribute('aria-label', playing ? '映像を一時停止' : '映像を再生');
    button.querySelector('[data-film-label]').textContent = playing ? '一時停止' : '再生';
    button.querySelector('[data-film-icon]').textContent = playing ? 'Ⅱ' : '▶';
  }
  function syncVideos() {
    videos.forEach(video => {
      const state = states.get(video);
      if (!canPlay(video)) { video.pause(); updateControl(video); return; }
      if (!video.paused || state.pending) return;
      if (!video.getAttribute('src')) { video.src = video.dataset.src; video.load(); }
      state.pending = true;
      Promise.resolve(video.play()).then(() => {
        if (!canPlay(video)) video.pause();
      }).catch(error => {
        if (error.name === 'NotAllowedError') state.blocked = true;
        if (error.name === 'AbortError') requestAnimationFrame(syncVideos);
      }).finally(() => { state.pending = false; updateControl(video); });
    });
  }
  function refreshVisibility() {
    videos.forEach(video => {
      const rect = video.getBoundingClientRect();
      const visibleHeight = Math.min(rect.bottom, window.innerHeight) - Math.max(rect.top, 0);
      states.get(video).visible = rect.width > 0 && rect.height > 0 && visibleHeight > Math.min(rect.height * .2, 150);
    });
    syncVideos();
  }
  videos.forEach(video => {
    video.muted = true;
    video.addEventListener('playing', () => { if (!canPlay(video)) video.pause(); updateControl(video); });
    video.addEventListener('pause', () => updateControl(video));
    video.addEventListener('error', () => {
      states.get(video).failed = true;
      const error = video.closest('.film-frame').querySelector('.film-error');
      if (error) error.hidden = false;
      updateControl(video);
    });
    document.querySelector(`[data-film-toggle="${video.id}"]`)?.addEventListener('click', () => {
      const state = states.get(video);
      if (!video.paused) { state.userPaused = true; state.userStarted = false; }
      else { state.userPaused = false; state.userStarted = true; state.blocked = false; }
      refreshVisibility();
    });
    document.querySelector(`[data-film-retry="${video.id}"]`)?.addEventListener('click', () => {
      const state = states.get(video);
      state.failed = false; state.blocked = false; state.userPaused = false; state.userStarted = true;
      video.closest('.film-frame').querySelector('.film-error').hidden = true;
      video.pause();
      video.removeAttribute('src');
      refreshVisibility();
    });
  });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => { states.get(entry.target).visible = entry.isIntersecting && entry.intersectionRatio >= .2; });
      syncVideos();
    }, { threshold: [0, .2, .5] });
    videos.forEach(video => observer.observe(video));
  } else {
    window.addEventListener('scroll', refreshVisibility, { passive: true });
    window.addEventListener('resize', refreshVisibility, { passive: true });
    refreshVisibility();
  }
  document.addEventListener('visibilitychange', syncVideos);
  reducedMotion.addEventListener('change', () => {
    states.forEach(state => { state.userStarted = false; });
    syncVideos();
  });

  function setMenu(open, restoreFocus = false) {
    if (!menuButton || !menu) return;
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    menu.classList.toggle('is-open', open);
    menu.inert = !open;
    main.inert = open;
    footer.inert = open;
    document.body.classList.toggle('menu-open', open);
    syncVideos();
    if (open) menu.querySelector('a')?.focus();
    else if (restoreFocus) menuButton.focus();
  }
  menuButton?.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true', true));
  menu?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', event => {
    if (menuButton?.getAttribute('aria-expanded') !== 'true') return;
    if (event.key === 'Escape') { event.preventDefault(); setMenu(false, true); }
    if (event.key === 'Tab') {
      const items = [menuButton, ...menu.querySelectorAll('a[href]')];
      const index = items.indexOf(document.activeElement);
      if (event.shiftKey && index <= 0) { event.preventDefault(); items.at(-1).focus(); }
      else if (!event.shiftKey && (index === items.length - 1 || index === -1)) { event.preventDefault(); items[0].focus(); }
    }
  });
  window.matchMedia('(min-width: 821px)').addEventListener('change', event => { if (event.matches) setMenu(false); });

  const tabActions = new Map();
  document.querySelectorAll('[role="tablist"]').forEach(list => {
    const tabs = [...list.querySelectorAll('[role="tab"]')];
    const select = (tab, focus = false) => {
      tabs.forEach(item => {
        const active = item === tab;
        item.setAttribute('aria-selected', String(active));
        item.tabIndex = active ? 0 : -1;
        document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
      });
      syncVideos();
      requestAnimationFrame(refreshVisibility);
      if (focus) {
        tab.focus();
        if (list.classList.contains('future-tabs')) {
          const left = tab.offsetLeft - list.offsetLeft;
          if (left < list.scrollLeft) list.scrollLeft = left;
          else if (left + tab.offsetWidth > list.scrollLeft + list.clientWidth) list.scrollLeft = left + tab.offsetWidth - list.clientWidth;
        }
      }
    };
    tabs.forEach((tab, index) => {
      tabActions.set(tab.id, () => select(tab));
      tab.addEventListener('click', () => select(tab));
      tab.addEventListener('keydown', event => {
        let next;
        if (['ArrowRight', 'ArrowDown'].includes(event.key)) next = (index + 1) % tabs.length;
        if (['ArrowLeft', 'ArrowUp'].includes(event.key)) next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next !== undefined) { event.preventDefault(); select(tabs[next], true); }
      });
    });
  });
  document.querySelectorAll('[data-open-tab]').forEach(link => {
    link.addEventListener('click', () => tabActions.get(link.dataset.openTab)?.());
  });

  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    const status = contactForm.querySelector('[data-form-status]');
    const submit = contactForm.querySelector('button[type="submit"]');
    const container = contactForm.parentElement;
    const setStatus = (state, text) => {
      status.hidden = !text;
      status.textContent = text || '';
      status.classList.remove('error', 'success');
      if (state) status.classList.add(state);
    };
    const showSuccess = () => {
      contactForm.hidden = true;
      const heading = container.querySelector('h2');
      const notes = container.querySelectorAll('.contact-note');
      const eyebrow = container.querySelector('.eyebrow');
      [heading, ...notes, eyebrow].forEach(node => { if (node) node.hidden = true; });
      const panel = document.createElement('div');
      panel.className = 'contact-success';
      panel.setAttribute('role', 'status');
      panel.setAttribute('aria-live', 'polite');
      panel.innerHTML = '<span class="contact-success-mark" aria-hidden="true">✓</span><h2>お問い合わせを受け付けました。</h2><p>担当より数営業日以内に折り返しご連絡いたします。<br>今しばらくお待ちください。</p><a class="text-link" href="/">トップページへ戻る <span aria-hidden="true">↗</span></a>';
      container.appendChild(panel);
      panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
      panel.focus?.();
    };
    contactForm.addEventListener('submit', async event => {
      event.preventDefault();
      if (!contactForm.reportValidity()) return;
      const data = Object.fromEntries(new FormData(contactForm).entries());
      submit.disabled = true;
      setStatus(null, '送信中です…');
      try {
        const response = await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(data)
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.error || '送信に失敗しました。時間を置いて再度お試しください。');
        contactForm.reset();
        showSuccess();
      } catch (error) {
        setStatus('error', error.message || '送信に失敗しました。時間を置いて再度お試しください。');
        submit.disabled = false;
      }
    });
  }
})();
