// 홈 화면을 data/site.json 으로 그린다. 글 목록은 scripts/update_site.py 가 네이버 블로그 RSS로 새로 쓴다.
(function () {
  var E = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var ext = function (u) { return /^https?:/.test(u) ? ' target="_blank" rel="noopener"' : ""; };
  var a = function (u, inner, cls) { return '<a' + (cls ? ' class="' + cls + '"' : "") + ' href="' + E(u) + '"' + ext(u) + '>' + inner + "</a>"; };
  var im = function (i, lazy) { return '<img src="' + E(i.src) + '" alt="' + E(i.alt) + '" width="' + i.w + '" height="' + i.h + '"' + (lazy ? ' loading="lazy"' : "") + ">"; };
  var head = function (s) { return '<div class="section-head"><div><span class="label">' + E(s.label) + "</span><h2>" + E(s.title) + "</h2></div>" + a(s.more.url, E(s.more.text), "more") + "</div>"; };
  var posts = function (list) {
    return '<ul class="posts">' + list.map(function (p) {
      return "<li>" + a(p.url, '<span class="pt">' + E(p.title) + '</span><span class="pd">' + E(p.date) + "</span>" + (p.sub ? '<span class="ps">' + E(p.sub) + "</span>" : "")) + "</li>";
    }).join("") + "</ul>";
  };
  var STATUS = { boarding: "탑승중", ontime: "정시" };

  var R = {
    hero: function (h) {
      return '<div class="wrap"><div class="hero-copy"><p class="eyebrow">' + E(h.eyebrow) + "</p><h1>" + h.titleHtml + '</h1><p class="lead">' + E(h.lead) + "</p>" +
        '<ul class="creds">' + h.creds.map(function (c) { return "<li>" + E(c) + "</li>"; }).join("") + "</ul>" +
        '<div class="hero-actions"><a class="btn" href="#trip">최근 글 읽기</a>' + a("https://www.youtube.com/@RunToriDaddy", "유튜브 @RunToriDaddy ↗", "btn ghost") + "</div></div>" +
        '<figure class="hero-photo">' + im(h.photo) + "<figcaption>" + h.photo.tags.map(function (t) { return "<span>" + E(t) + "</span>"; }).join("") + "</figcaption></figure></div>";
    },
    board: function (b) {
      return '<div class="wrap"><div class="board"><div class="board-top"><h2 id="board-title">DEPARTURES<small>오늘은 어디로 떠나볼까요</small></h2>' +
        '<span class="board-clock" id="clock">SEOUL ICN · KST</span></div><div class="board-scroll"><table><thead><tr><th scope="col">편명</th><th scope="col">행선지</th>' +
        '<th scope="col">최근 글</th><th scope="col">출발</th><th scope="col">상태</th></tr></thead><tbody>' +
        b.rows.map(function (r) {
          return '<tr class="row" data-href="' + E(r.url) + '"><td class="flight">' + E(r.code) + '</td><td class="dest">' + E(r.dest) + '</td><td class="post">' + a(r.url, E(r.title)) +
            '</td><td class="when">' + E(r.date) + '</td><td class="status ' + E(r.status) + '">' + (STATUS[r.status] || "") + "</td></tr>";
        }).join("") + '</tbody></table></div><p class="board-foot">' + E(b.foot) + "</p></div></div>";
    },
    trip: function (t) {
      return '<div class="wrap">' + head(t) + '<div class="trip"><figure>' + im(t.figure, true) + "<figcaption>" + E(t.figure.caption) + '</figcaption></figure><ol class="itin">' +
        t.days.map(function (d) {
          return "<li>" + a(d.url, '<span class="d"><b>' + E(d.day) + "</b>" + E(d.date) + '</span><span class="t">' + E(d.title) + '</span><span class="place">' + E(d.place) + '</span><span class="p">' + E(d.text) + "</span>") + "</li>";
        }).join("") + "</ol></div></div>";
    },
    log: function (l) {
      var p = l.project;
      return '<div class="wrap"><div class="log-head"><div><span class="label">' + E(l.label) + "</span><h2>" + E(l.title) + "</h2><p>" + E(l.text) + '</p></div><dl class="stats">' +
        l.stats.map(function (s) { return "<div><dt>" + E(s.k) + "</dt><dd>" + E(s.v) + "</dd></div>"; }).join("") + '</dl></div><div class="strip">' +
        l.strip.map(function (s) { return a(s.url, im(s, true) + '<div class="cap"><span>' + E(s.title) + "</span><span>" + E(s.meta) + "</span></div>"); }).join("") +
        '</div><div class="mapnote">' + im(p, true) + '<div><span class="label">' + E(p.label) + "</span><h3>" + E(p.title) + "</h3><p>" + E(p.text) + "</p>" +
        '<div style="display:flex;flex-wrap:wrap;gap:12px 24px">' + p.links.map(function (k) { return a(k.url, E(k.text), "more"); }).join("") + "</div></div></div></div>";
    },
    ai: function (x) {
      return '<div class="wrap">' + head(x) + '<div class="ai"><div class="ai-hook"><div class="year">' + E(x.hook.year) + "</div><blockquote>" + E(x.hook.quote) + "</blockquote>" +
        '<p class="src">' + E(x.hook.text) + " " + a(x.hook.link.url, E(x.hook.link.text)) + "</p></div>" + posts(x.posts) + "</div></div>";
    },
    book: function (b) {
      return '<div class="wrap">' + im(b, true) + '<div class="book-copy"><span class="label">' + E(b.label) + "</span><h2>" + E(b.title) + '</h2><p class="sub">' + E(b.sub) + '</p><ol class="chapters">' +
        b.chapters.map(function (c) {
          return "<li" + (c.todo ? ' class="todo"' : "") + ">" + a(c.url, '<span class="cn">' + E(c.no) + '</span><span class="ct">' + E(c.title) + '</span><span class="cd">' + E(c.date) + "</span>") + "</li>";
        }).join("") + "</ol></div></div>";
    },
    columns: function (cs) {
      return '<div class="wrap two">' + cs.map(function (c) {
        return '<div class="col"><span class="label">' + E(c.label) + "</span><h3>" + E(c.title) + "</h3><p>" + E(c.text) + "</p>" + posts(c.posts) + "</div>";
      }).join("") + "</div>";
    },
    foot: function (s) { return E(s.footNote); }
  };

  function wire() {
    // 출발 안내판: 행 전체를 누를 수 있고, 키보드는 안쪽 링크로 간다
    document.querySelectorAll(".board tr.row").forEach(function (row) {
      row.addEventListener("click", function (e) { if (!e.target.closest("a")) row.querySelector("a").click(); });
    });
    var clock = document.getElementById("clock");
    function tick() {
      try {
        clock.textContent = "SEOUL ICN · " + new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date()) + " KST";
      } catch (e) {}
    }
    if (clock) { tick(); setInterval(tick, 30000); }
    if (location.hash) { var t = document.querySelector(location.hash); if (t) t.scrollIntoView(); }
  }

  fetch("data/site.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (s) {
    document.querySelectorAll("[data-mount]").forEach(function (el) {
      var k = el.getAttribute("data-mount");
      el.innerHTML = R[k](k === "foot" ? s : s[k]);
    });
    wire();
  }).catch(function (e) {
    var h = document.querySelector('[data-mount="hero"]');
    if (h) h.innerHTML = '<div class="wrap"><p class="lead">글 목록을 불러오지 못했습니다. <a href="https://blog.naver.com/joekang">네이버 블로그</a>에서 읽어 주세요.</p></div>';
  });
})();
