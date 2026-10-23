"""블로그 홈을 동적으로 바꾼다(한 번만): index.html 의 내용을 data/site.json 으로 옮기고, 자리만 남긴다.
화면은 assets/app.js 가 site.json 을 받아 같은 마크업으로 그린다. 다시 돌리면 아무 일도 하지 않는다.
"""
import html as H, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX, DATA = ROOT / "index.html", ROOT / "data/site.json"
src = INDEX.read_text(encoding="utf-8")
if 'src="assets/app.js"' in src:
    raise SystemExit("이미 동적입니다")

def sec(start: str, end: str) -> str:
    i = src.index(start); return src[i:src.index(end, i)]
def txt(s: str) -> str:
    return H.unescape(re.sub(r"<[^>]+>", "", s)).strip()
def one(p: str, s: str) -> str:
    m = re.search(p, s, re.S); return m.group(1) if m else ""
def img(s: str) -> dict:
    t = re.search(r"<img ([^>]+)>", s).group(1)
    a = dict(re.findall(r'(\w+)="([^"]*)"', t))
    return {"src": a["src"], "alt": H.unescape(a["alt"]), "w": int(a["width"]), "h": int(a["height"])}

hero = sec('<section class="hero">', "</section>")
board = sec('<section id="board"', "</section>")
trip = sec('<section id="trip"', "</section>")
log = sec('<section id="log"', "</section>")
ai = sec('<section id="ai"', "</section>")
book = sec('<section id="book"', "</section>")
cols = sec('<!-- ESSAYS & FAITH -->', "</section>")
foot = one(r'<footer>.*?<small>(.*?)</small>', src)

site = {
    "updated": one(r"(\d{4}\.\d{2}\.\d{2}) 기준", foot),
    "footNote": txt(foot),
    "hero": {"eyebrow": txt(one(r'<p class="eyebrow">(.*?)</p>', hero)),
             "titleHtml": one(r"<h1>(.*?)</h1>", hero),
             "lead": txt(one(r'<p class="lead">(.*?)</p>', hero)),
             "creds": [txt(x) for x in re.findall(r"<li>(.*?)</li>", one(r'<ul class="creds">(.*?)</ul>', hero), re.S)],
             "photo": {**img(one(r'(<figure class="hero-photo">.*?</figure>)', hero)),
                       "tags": [txt(x) for x in re.findall(r"<span>(.*?)</span>", one(r"<figcaption>(.*?)</figcaption>", hero))]}},
    "board": {"foot": txt(one(r'<p class="board-foot">(.*?)</p>', board)),
              "rows": [{"code": txt(c), "dest": txt(d), "url": u, "title": txt(t), "date": txt(w), "status": s}
                       for u, c, d, t, w, s in re.findall(
                           r'<tr class="row" data-href="([^"]+)">\s*<td class="flight">(.*?)</td><td class="dest">(.*?)</td>\s*'
                           r'<td class="post">(.*?)</td>\s*<td class="when">(.*?)</td><td class="status (\w+)">', board, re.S)]},
    "trip": {"label": txt(one(r'<span class="label">(.*?)</span>', trip)), "title": txt(one(r"<h2>(.*?)</h2>", trip)),
             "more": {"text": txt(one(r'<a class="more"[^>]*>(.*?)</a>', trip)), "url": one(r'<a class="more" href="([^"]+)"', trip)},
             "figure": {**img(one(r"(<figure>.*?</figure>)", trip)), "caption": txt(one(r"<figcaption>(.*?)</figcaption>", trip))},
             "days": [{"url": u, "day": txt(dd), "date": txt(dt), "title": txt(t), "place": txt(p), "text": txt(x)}
                      for u, dd, dt, t, p, x in re.findall(
                          r'<li><a href="([^"]+)"[^>]*>\s*<span class="d"><b>(.*?)</b>(.*?)</span>\s*<span class="t">(.*?)</span>\s*'
                          r'<span class="place">(.*?)</span>\s*<span class="p">(.*?)</span>', trip, re.S)]},
    "log": {"label": txt(one(r'<span class="label">(.*?)</span>', log)), "title": txt(one(r"<h2>(.*?)</h2>", log)),
            "text": txt(one(r'<h2>.*?</h2>\s*<p>(.*?)</p>', log)),
            "stats": [{"k": txt(k), "v": txt(v)} for k, v in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", log)],
            "strip": [{"url": u, **img(i), "title": txt(t), "meta": txt(m)} for u, i, t, m in re.findall(
                r'<a href="([^"]+)"[^>]*>\s*(<img [^>]+>)\s*<div class="cap"><span>(.*?)</span><span>(.*?)</span>', log, re.S)],
            "project": {**img(one(r'(<div class="mapnote">.*?</div>)', log)),
                        "label": txt(one(r'<div class="mapnote">.*?<span class="label">(.*?)</span>', log)),
                        "title": txt(one(r"<h3>(.*?)</h3>", log)), "text": txt(one(r"</h3>\s*<p>(.*?)</p>", log)),
                        "links": [{"url": u, "text": txt(t)} for u, t in re.findall(r'<a class="more" href="([^"]+)"[^>]*>(.*?)</a>', log)]}},
    "ai": {"label": txt(one(r'<span class="label">(.*?)</span>', ai)), "title": txt(one(r"<h2>(.*?)</h2>", ai)),
           "more": {"text": txt(one(r'<a class="more"[^>]*>(.*?)</a>', ai)), "url": one(r'<a class="more" href="([^"]+)"', ai)},
           "hook": {"year": txt(one(r'<div class="year">(.*?)</div>', ai)), "quote": txt(one(r"<blockquote>(.*?)</blockquote>", ai)),
                    "text": txt(one(r'<p class="src">(.*?)<a', ai)),
                    "link": {"url": one(r'<p class="src">.*?href="([^"]+)"', ai), "text": txt(one(r'<p class="src">.*?<a[^>]*>(.*?)</a>', ai))}},
           "posts": [{"url": u, "title": txt(t), "date": txt(d), "sub": txt(s or "")} for u, t, d, s in re.findall(
               r'<li><a href="([^"]+)"[^>]*>\s*<span class="pt">(.*?)</span><span class="pd">(.*?)</span>(?:\s*<span class="ps">(.*?)</span>)?</a></li>', ai, re.S)]},
    "book": {**img(book), "label": txt(one(r'<span class="label">(.*?)</span>', book)), "title": txt(one(r"<h2>(.*?)</h2>", book)),
             "sub": txt(one(r'<p class="sub">(.*?)</p>', book)),
             "chapters": [{"todo": bool(c), "url": u, "no": txt(n), "title": txt(t), "date": txt(d)} for c, u, n, t, d in re.findall(
                 r'<li( class="todo")?><a href="([^"]+)"[^>]*><span class="cn">(.*?)</span><span class="ct">(.*?)</span><span class="cd">(.*?)</span>', book)]},
    "columns": [{"label": txt(l), "title": txt(t), "text": txt(p), "category": c,
                 "posts": [{"url": u, "title": txt(pt), "date": txt(pd)} for u, pt, pd in re.findall(
                     r'<li><a href="([^"]+)"[^>]*><span class="pt">(.*?)</span><span class="pd">(.*?)</span></a></li>', ul)]}
                for (l, t, p, ul), c in zip(re.findall(r'<span class="label">(.*?)</span>\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>\s*<ul class="posts">(.*?)</ul>', cols, re.S),
                                            ["일상 생각,에세이", "신앙생활"])],
}
site["ai"]["category"] = "AI , Tech 인사이트"
# 빠짐없이 옮겼는지
assert len(site["board"]["rows"]) == 6 and len(site["trip"]["days"]) == 7 and len(site["log"]["strip"]) == 4, "목록을 다 못 옮김"
assert len(site["ai"]["posts"]) == 6 and len(site["book"]["chapters"]) == 5 and [len(c["posts"]) for c in site["columns"]] == [3, 3]
DATA.parent.mkdir(exist_ok=True)
DATA.write_text(json.dumps(site, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# index.html: 내용 자리를 비우고 data-mount 만 남긴다
out = src
for whole, mount in [(hero, '<section class="hero" data-mount="hero"></section>'), (board, '<section id="board" class="board-wrap" aria-labelledby="board-title" data-mount="board"></section>'),
                     (trip, '<section id="trip" class="section" data-mount="trip"></section>'), (log, '<section id="log" class="band section" data-mount="log"></section>'),
                     (ai, '<section id="ai" class="section" data-mount="ai"></section>'), (book, '<section id="book" class="book section" data-mount="book"></section>')]:
    out = out.replace(whole + "</section>", mount)
out = out.replace(cols + "</section>", '<!-- ESSAYS & FAITH -->\n  <section class="section" data-mount="columns"></section>')
out = out.replace(f"<small>{foot}</small>", '<small data-mount="foot"></small>')
script = out[out.index("<script>\n  // Board rows"):out.index("</body>")]
out = out.replace(script, '<script src="assets/app.js" defer></script>\n')
INDEX.write_text(out, encoding="utf-8")
print(f"옮김 → {DATA.relative_to(ROOT)} · index.html {len(src)//1024}KB → {len(out)//1024}KB")
