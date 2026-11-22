/* YayPicks – site helpers (loaded by the theme from jsDelivr).
   1) Post pages: "More picks like this" (same subcategory, then main category) + Black Friday banner during the event.
   2) Label pages: subcategory chips under the heading.
   No prices are shown anywhere. */
(function () {
  var CATS = {
    'Tech': ['Headphones & Speakers', 'Computer Accessories', 'Gadgets & Smart Home'],
    'Home & Kitchen': ['Kitchen Appliances', 'Cookware & Kitchen Tools', 'Drinkware & Coffee', 'Home Care & Comfort'],
    'Beauty': ['Skincare', 'Hair Care', 'Makeup']
  };
  var SUB2MAIN = {};
  Object.keys(CATS).forEach(function (m) { CATS[m].forEach(function (s) { SUB2MAIN[s] = m; }); });
  var EVENT_END = Date.parse('2026-12-01T10:00:00+03:00');

  var css = '' +
    '.spd-rel{margin:44px 0 0;padding-top:28px;border-top:1px solid #e8e8ed}.spd-rel h2{font-size:26px!important;letter-spacing:-.5px;margin:0 0 16px!important}' +
    '.spd-rel-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}' +
    '.spd-rel a.spd-rc{display:flex;flex-direction:column;border:1px solid #e8e8ed;border-radius:18px;overflow:hidden;color:#1d1d1f!important;text-decoration:none!important;background:#fff}' +
    '.spd-rc-img{aspect-ratio:1/1;background:#f5f5f7}.spd-rc-img img{width:100%;height:100%;object-fit:cover;display:block;border-radius:0!important}' +
    '.spd-rc b{display:block;font-size:14px;line-height:1.3;padding:10px 12px 12px}' +
    '.spd-bf{display:block;margin:22px 0 0;padding:16px 20px;border-radius:18px;background:#1d1d1f;color:#fff!important;text-decoration:none!important;font-weight:600}' +
    '.spd-bf span{display:block;font-weight:400;font-size:14px;opacity:.8}' +
    '.spd-chips{display:flex;flex-wrap:wrap;gap:8px;margin:-6px 0 22px}.spd-chips a{background:#f5f5f7;border-radius:999px;padding:7px 14px;font-size:14px;font-weight:600;color:#1d1d1f!important;text-decoration:none!important}' +
    '.spd-chips a.on{background:#1d1d1f;color:#fff!important}' +
    '.nav .wrap .nav-links{margin-left:28px}' +
    '@media(max-width:640px){.nav .wrap{padding:0 14px}.brand{font-size:15px!important;white-space:nowrap;gap:7px!important}.nav-search{margin-left:auto!important;margin-right:6px!important}.nav-search input{width:92px!important}.nav-search input:focus{width:120px!important}.nav-cta{white-space:nowrap;font-size:12px!important;padding:6px 10px!important}}' +
    '@media(max-width:700px){.spd-rel-grid{grid-template-columns:repeat(2,1fr)}}' +
    '.spd-buy{position:fixed;left:10px;right:10px;bottom:10px;z-index:60;display:none;align-items:center;gap:10px;background:#1d1d1f;color:#fff;border-radius:18px;padding:10px 10px 10px 16px;box-shadow:0 8px 30px rgba(0,0,0,.25);transform:translateY(140%);transition:transform .25s ease}' +
    '.spd-buy.show{transform:none}.spd-buy b{flex:1;font-size:14px;line-height:1.25;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}' +
    '.spd-buy a{background:#b6e324;color:#1d1d1f!important;font-weight:700;font-size:14px;padding:11px 14px;border-radius:12px;white-space:nowrap;text-decoration:none!important}' +
    '.spd-buy small{display:block;font-size:10px;opacity:.6;font-weight:400}' +
    '@media(max-width:760px){.spd-buy{display:flex}body.spd-has-buy{padding-bottom:84px}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  function esc(s) { return String(s || '').replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function labelUrl(l) { return '/search/label/' + encodeURIComponent(l); }

  // ---- Label pages: chips
  var q = (location.search.match(/[?&]q=([^&]+)/) || [])[1];
  var h2 = document.querySelector('#picks .sec-head h2');
  if (h2 && q && location.pathname === '/search') h2.textContent = 'Results for \u201c' + decodeURIComponent(q.replace(/\+/g, ' ')) + '\u201d';
  var m = location.pathname.match(/^\/search\/label\/([^/?#]+)/);
  if (m) {
    var cur = decodeURIComponent(m[1]);
    if (h2) h2.textContent = cur;
    /* page title is set server-side by the theme (SEO) */
    var main = CATS[cur] ? cur : SUB2MAIN[cur];
    var head = document.querySelector('#picks .sec-head');
    if (main && head) {
      var html = '<a href="' + labelUrl(main) + '"' + (cur === main ? ' class="on"' : '') + '>All ' + esc(main) + '</a>' +
        CATS[main].map(function (s) { return '<a href="' + labelUrl(s) + '"' + (s === cur ? ' class="on"' : '') + '>' + esc(s) + '</a>'; }).join('');
      var div = document.createElement('div'); div.className = 'spd-chips'; div.innerHTML = html;
      head.parentNode.insertBefore(div, head.nextSibling);
    }
  }

  // ---- Nav: Gift Guides link
  var nl = document.querySelector('.nav-links');
  if (nl && !nl.querySelector('a[href*="Gift%20Guides"]')) {
    var g = document.createElement('a'); g.href = '/search/label/Gift%20Guides'; g.textContent = 'Gift Guides';
    nl.insertBefore(g, nl.firstChild);
  }

  // ---- Post pages: sticky "Check it on Amazon" bar (mobile), single-product reviews only
  (function () {
    var b = document.querySelector('article.article .post-body');
    if (!b || !/\/\d{4}\/\d{2}\//.test(location.pathname)) return;
    var links = [].slice.call(b.querySelectorAll('a[href*="amazon.com/dp/"]'));
    var asins = {}; links.forEach(function (a) { var m = a.href.match(/\/dp\/([A-Z0-9]{10})/); if (m) asins[m[1]] = a.href; });
    var keys = Object.keys(asins);
    if (keys.length !== 1) return;
    var h1 = document.querySelector('article.article h1');
    var name = (h1 ? h1.textContent : '').split(/:| Review| – | - /)[0].trim();
    var bar = document.createElement('div'); bar.className = 'spd-buy';
    bar.innerHTML = '<b>' + esc(name) + '<small>As an Amazon Associate we earn from qualifying purchases.</small></b>' +
      '<a target="_blank" rel="nofollow sponsored noopener" href="' + esc(asins[keys[0]]) + '">Check it on Amazon</a>';
    document.body.appendChild(bar); document.body.classList.add('spd-has-buy');
    var shown = false;
    function onScroll() { var y = window.scrollY || 0; var s = y > 500; if (s !== shown) { shown = s; bar.classList.toggle('show', s); } }
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  })();

  // ---- Post pages: related picks
  var body = document.querySelector('article.article .post-body');
  if (!body || !/\/\d{4}\/\d{2}\//.test(location.pathname)) return;
  var labels = [].map.call(document.querySelectorAll('article.article .meta a.chip'), function (a) { return a.textContent.trim(); });
  var sub = labels.filter(function (l) { return SUB2MAIN[l]; })[0];
  var main2 = sub ? SUB2MAIN[sub] : labels.filter(function (l) { return CATS[l]; })[0];
  if (!sub && !main2) return;
  var here = location.pathname;

  function fetchLabel(l) {
    return fetch('/feeds/posts/default/-/' + encodeURIComponent(l) + '?alt=json&max-results=9')
      .then(function (r) { return r.json(); })
      .then(function (j) {
        return (j.feed.entry || []).map(function (e) {
          var link = (e.link.filter(function (k) { return k.rel === 'alternate'; })[0] || {}).href || '';
          var img = ((e.content && e.content.$t) || '').match(/<img[^>]+src="([^"]+)"/);
          return { url: link, title: e.title.$t, img: img ? img[1] : '' };
        });
      }).catch(function () { return []; });
  }

  var wanted = [sub, main2].filter(Boolean);
  Promise.all(wanted.map(fetchLabel)).then(function (lists) {
    var seen = {}, out = [];
    lists.forEach(function (list) {
      list.forEach(function (p) {
        var path = p.url.replace(/^https?:\/\/[^/]+/, '');
        if (!p.url || path === here || seen[path] || out.length >= 4) return;
        seen[path] = 1; out.push(p);
      });
    });
    if (!out.length) return;
    var sec = document.createElement('section');
    sec.className = 'spd-rel';
    sec.innerHTML = '<h2>More ' + esc(sub || main2) + ' picks</h2><div class="spd-rel-grid">' +
      out.map(function (p) {
        var path = p.url.replace(/^https?:\/\/[^/]+/, '');
        return '<a class="spd-rc" href="' + esc(path) + '"><div class="spd-rc-img">' + (p.img ? '<img loading="lazy" alt="" src="' + esc(p.img) + '">' : '') + '</div><b>' + esc(p.title) + '</b></a>';
      }).join('') + '</div>' +
      (Date.now() < EVENT_END ? '<a class="spd-bf" href="/p/black-friday-deals.html">Black Friday Week picks ›<span>Gift ideas from our reviews, with confirmed deals marked</span></a>' : '');
    body.parentNode.appendChild(sec);
  });
})();
