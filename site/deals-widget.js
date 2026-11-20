/* Smart Picks Daily – deals showcase (reads deals.json from GitHub).
   Home page: auto-scrolling strip above "Latest picks".
   /p/black-friday-deals.html: full grid inside #dsp-deals-full.
   Items vanish on their own after "expires"; whole widget hides after event.ends. */
(function () {
  var REPO = 'https://raw.githubusercontent.com/xoqxs/smart-picks-daily/main/';
  var DISCLOSURE = 'As an Amazon Associate I earn from qualifying purchases.';
  var path = location.pathname;
  var isHome = (path === '/' || path === '/index.html') && !location.search.match(/[?&](q|label|updated-max)=/);
  var full = document.getElementById('dsp-deals-full');
  if (!isHome && !full) { addNav(); return; }

  var css = '' +
    '.dspd{margin:36px auto 8px}.dspd-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:14px}' +
    '.dspd-head h2{font-size:28px;font-weight:700;letter-spacing:-.6px;margin:0;color:#1d1d1f}.dspd-head p{margin:4px 0 0;color:#6e6e73;font-size:14px}' +
    '.dspd-all{white-space:nowrap;background:#1d1d1f;color:#fff!important;border-radius:999px;padding:9px 16px;font-weight:600;font-size:14px;text-decoration:none}' +
    '.dspd-wrap{position:relative}.dspd-track{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;padding:2px 2px 12px;-webkit-overflow-scrolling:touch;scrollbar-width:none}' +
    '.dspd-track::-webkit-scrollbar{display:none}.dspd-card{flex:0 0 210px;scroll-snap-align:start;border:1px solid #e8e8ed;border-radius:22px;background:#fff;overflow:hidden;display:flex;flex-direction:column}' +
    '.dspd-img{position:relative;aspect-ratio:1/1;background:#f5f5f7;display:block}.dspd-img img{width:100%;height:100%;object-fit:contain;display:block}' +
    '.dspd-badge{position:absolute;top:10px;left:10px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;padding:4px 9px;border-radius:999px;background:#1d1d1f;color:#fff}' +
    '.dspd-badge.deal{background:#d70015}.dspd-body{padding:12px 14px 14px;display:flex;flex-direction:column;gap:8px;flex:1}' +
    '.dspd-name{font-size:15px;font-weight:600;line-height:1.3;color:#1d1d1f;margin:0}.dspd-cat{font-size:12px;color:#6e6e73}' +
    '.dspd-btn{margin-top:auto;display:block;text-align:center;background:#0071e3;color:#fff!important;border-radius:999px;padding:9px 10px;font-weight:600;font-size:14px;text-decoration:none}' +
    '.dspd-rev{display:block;text-align:center;font-size:13px;color:#0066cc!important;text-decoration:none}.dspd-cr{font-size:10px;color:#86868b;text-align:right}' +
    '.dspd-nav{position:absolute;top:38%;width:38px;height:38px;border-radius:50%;border:1px solid #e8e8ed;background:rgba(255,255,255,.95);font-size:20px;line-height:1;cursor:pointer;color:#1d1d1f;display:none}' +
    '.dspd-prev{left:-10px}.dspd-next{right:-10px}@media(min-width:760px){.dspd-nav{display:block}}' +
    '.dspd-disc{font-size:12px;color:#86868b;margin:6px 0 0}.dspd-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px}' +
    '.dspd-grid .dspd-card{flex:none}.dspd-event{display:block;margin:18px 0;padding:18px 20px;border-radius:22px;background:#1d1d1f;color:#fff!important;text-decoration:none}' +
    '.dspd-event b{display:block;font-size:20px}.dspd-event span{font-size:14px;opacity:.8}' +
    '.nav-links a.dspd-navlink{color:#d70015!important;font-weight:700}' +
    '@media(max-width:560px){.dspd-grid{grid-template-columns:repeat(2,1fr);gap:10px}.dspd-card{flex-basis:168px}.dspd-body{padding:10px 11px 12px}.dspd-name{font-size:14px}.dspd-btn{font-size:13px;padding:8px 6px}.dspd-head h2{font-size:22px}}';

  addNav();
  var bust = Math.floor(Date.now() / 600000);
  fetch(REPO + 'deals.json?t=' + bust).then(function (r) { return r.json(); }).then(render).catch(function () {});

  function addNav() {
    var nav = document.querySelector('.nav-links');
    if (!nav || nav.querySelector('.dspd-navlink')) return;
    if (Date.now() > Date.parse('2026-12-01T10:00:00+03:00')) return;
    var a = document.createElement('a');
    a.href = '/p/black-friday-deals.html'; a.className = 'dspd-navlink'; a.textContent = 'Black Friday';
    nav.insertBefore(a, nav.firstChild);
  }

  function esc(s) { return String(s || '').replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function okUrl(u) { return /^https:\/\/(www\.amazon\.com|smartpicksdaily-reviews\.blogspot\.com|[a-z0-9.-]+\.[a-z]{2,})\//.test(u || ''); }

  function card(it) {
    var amz = okUrl(it.amazon) ? it.amazon : '#';
    var img = /^https?:/.test(it.img) ? it.img : REPO + it.img;
    var label = it.badge === 'deal' ? 'Deal' : 'Gift pick';
    return '<div class="dspd-card">' +
      '<a class="dspd-img" href="' + esc(amz) + '" target="_blank" rel="nofollow sponsored noopener"><img loading="lazy" alt="' + esc(it.name) + '" src="' + esc(img) + '">' +
      '<span class="dspd-badge ' + (it.badge === 'deal' ? 'deal' : '') + '">' + label + '</span></a>' +
      '<div class="dspd-body"><span class="dspd-cat">' + esc(it.cat) + (it.note ? ' · ' + esc(it.note) : '') + '</span>' +
      '<p class="dspd-name">' + esc(it.name) + '</p>' +
      '<a class="dspd-btn" href="' + esc(amz) + '" target="_blank" rel="nofollow sponsored noopener">See today\'s price</a>' +
      (okUrl(it.post) ? '<a class="dspd-rev" href="' + esc(it.post) + '">Read our review ›</a>' : '') +
      (it.credit ? '<span class="dspd-cr">Image: ' + esc(it.credit) + '</span>' : '') +
      '</div></div>';
  }

  function render(data) {
    var now = Date.now();
    var ev = data.event || {};
    if (ev.ends && now > Date.parse(ev.ends)) return;
    var items = (data.items || []).filter(function (it) { return !it.expires || Date.parse(it.expires) > now; });
    if (!items.length) return;
    items.sort(function (a, b) { return (b.badge === 'deal') - (a.badge === 'deal'); });
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    var evLink = ev.url ? '<a class="dspd-event" href="' + esc(ev.url) + '" target="_blank" rel="nofollow sponsored noopener"><b>' + esc(ev.title || 'Shop all deals on Amazon') + ' ›</b><span>' + esc(ev.dates || '') + ' · Shop every deal on Amazon</span></a>' : '';

    if (full) {
      full.innerHTML = evLink + '<div class="dspd-grid">' + items.map(card).join('') + '</div><p class="dspd-disc">' + DISCLOSURE + ' Prices change often; check the current price on Amazon.</p>';
      return;
    }
    var anchor = document.getElementById('picks');
    if (!anchor) return;
    var sec = document.createElement('section');
    sec.className = 'wrap dspd';
    sec.innerHTML = '<div class="dspd-head"><div><h2>' + esc(ev.name || 'Deals') + ' picks</h2><p>Gift ideas from our reviews' + (ev.dates ? ' · ' + esc(ev.dates) : '') + '</p></div>' +
      '<a class="dspd-all" href="/p/black-friday-deals.html">See all ›</a></div>' +
      '<div class="dspd-wrap"><button class="dspd-nav dspd-prev" aria-label="Previous">‹</button><div class="dspd-track">' + items.map(card).join('') + '</div>' +
      '<button class="dspd-nav dspd-next" aria-label="Next">›</button></div><p class="dspd-disc">' + DISCLOSURE + '</p>';
    anchor.parentNode.insertBefore(sec, anchor);

    var track = sec.querySelector('.dspd-track');
    function step(dir) {
      var c = track.querySelector('.dspd-card'); if (!c) return;
      var w = c.getBoundingClientRect().width + 14;
      var max = track.scrollWidth - track.clientWidth - 4;
      if (dir > 0 && track.scrollLeft >= max) track.scrollTo({ left: 0 });
      else track.scrollBy({ left: dir * w });
    }
    sec.querySelector('.dspd-prev').onclick = function () { step(-1); };
    sec.querySelector('.dspd-next').onclick = function () { step(1); };
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var paused = false;
    ['mouseenter', 'touchstart', 'focusin'].forEach(function (e) { track.addEventListener(e, function () { paused = true; }, { passive: true }); });
    track.addEventListener('mouseleave', function () { paused = false; });
    setInterval(function () { if (!paused && !document.hidden) step(1); }, 3200);
  }
})();
