// App shell: wraps <main data-shell> content with sidebar + topbar.
// Usage: <body data-page="dashboard"> <main data-shell> ...page content... </main> <script src="assets/demo-data.js"></script><script src="assets/shell.js"></script>
(function () {
  const I = {
    home: '<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    find: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    spend: '<path d="M4 19V9M10 19V5M16 19v-7M22 19H2"/>',
    ai: '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
    cal: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    chat: '<path d="M4 5h16v11H8l-4 4z"/>',
    doc: '<path d="M6 3h9l5 5v13H6z"/><path d="M14 3v6h6M9 13h7M9 17h7"/>',
    plug: '<path d="M9 7V3M15 7V3M7 7h10v4a5 5 0 0 1-10 0zM12 16v5"/>',
    mcp: '<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.3 11l7.4-3.8M8.3 13l7.4 3.8"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    bell: '<path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10 21a2 2 0 0 0 4 0"/>',
  };
  const svg = (k) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${I[k]}</svg>`;
  window.icon = svg;

  const D = window.DEMO;
  const open = D ? D.findings.filter(f => f.status === 'open').length : 0;
  const NAV = [
    ['ראשי', [
      ['dashboard', 'app-dashboard.html', 'לוח בקרה', 'home'],
      ['findings', 'app-findings.html', 'ממצאים', 'find', open],
      ['spend', 'app-spend.html', 'הוצאות וספקים', 'spend'],
      ['ai', 'app-ai-spend.html', 'AI וטוקנים', 'ai'],
      ['renewals', 'app-renewals.html', 'חידושים', 'cal'],
    ]],
    ['עבודה', [
      ['agent', 'app-agent.html', 'הסוכן', 'chat'],
      ['report', 'app-report.html', 'דוחות', 'doc'],
    ]],
    ['חיבורים', [
      ['integrations', 'integrations.html', 'אינטגרציות', 'plug'],
      ['mcp', 'mcp.html', 'MCP וסוכנים', 'mcp'],
      ['settings', 'app-settings.html', 'הגדרות', 'gear'],
    ]],
  ];
  const page = document.body.dataset.page;
  const main = document.querySelector('[data-shell]');
  if (!main) return;

  const logo = `<svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2EE6A8"/><stop offset="1" stop-color="#5B9DFF"/></linearGradient></defs><circle cx="14" cy="14" r="10" fill="none" stroke="url(#lg)" stroke-width="3.2"/><path d="M21.5 21.5L28 28" stroke="url(#lg)" stroke-width="3.6" stroke-linecap="round"/><path d="M10 10v6.5a2 2 0 0 0 2 2h3.5M18 18V11.5a2 2 0 0 0-2-2h-3.5" fill="none" stroke="#EAF0F6" stroke-width="1.9" stroke-linecap="round"/></svg>`;
  window.LOGO = logo;

  const side = `<aside class="side">
    <a class="brand" href="landing.html">${logo}<span>איפה הכסף</span></a>
    <div class="ws"><span class="av">ט</span><div class="grow"><div style="font-weight:700">${D ? D.company.name : ''}</div><div class="xs muted">${D ? D.company.employees + ' עובדים · ' + D.company.stage : ''}</div></div></div>
    ${NAV.map(([sec, items]) => `<div class="sec">${sec}</div>` + items.map(([id, href, label, ic, count]) =>
      `<a class="nav-link" href="${href}" ${id === page ? 'aria-current="page"' : ''}>${svg(ic)}<span>${label}</span>${count ? `<span class="count">${count}</span>` : ''}</a>`).join('')).join('')}
    <div style="margin-top:auto" class="card flat small" >
      <div class="row between"><span class="muted xs">סריקה אחרונה</span><span class="chip fixed xs"><span class="dot"></span>חי</span></div>
      <div class="xs ink2" style="margin-top:6px">היום 08:14 · 155,263 שורות · 11 מקורות</div>
    </div>
  </aside>`;
  const top = `<header class="topbar">
    <div class="search">${svg('find')}<span>חפשו ספק, ממצא, חשבונית, או שאלו את הסוכן…</span><span class="kbd">Ctrl K</span></div>
    <div class="row" style="margin-inline-start:auto">
      <button class="btn ghost sm" aria-label="התראות">${svg('bell')}</button>
      <div class="row"><div class="avatar">${D ? D.user.initials : ''}</div><div class="small"><div style="font-weight:600">${D ? D.user.name : ''}</div><div class="xs muted">${D ? D.user.role : ''}</div></div></div>
    </div>
  </header>`;

  const wrap = document.createElement('div');
  wrap.className = 'app';
  wrap.innerHTML = side + `<div class="main">${top}</div>`;
  main.parentNode.insertBefore(wrap, main);
  main.classList.add('content');
  wrap.querySelector('.main').appendChild(main);
  const tag = document.createElement('div');
  tag.className = 'synthetic'; tag.textContent = 'נתונים סינתטיים · הדגמה';
  document.body.appendChild(tag);
})();
