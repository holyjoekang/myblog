"""네이버 블로그 RSS로 index.html 출발 안내판(최근 글)을 새로 쓴다.

    python scripts/update_board.py
"""
import email.utils, re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

RSS = "https://rss.blog.naver.com/joekang.xml"
INDEX = Path(__file__).resolve().parent.parent / "index.html"
CATS = {"달리기,여행,맛집": "TRV", "일상 생각,에세이": "ESY", "독서,책": "BKS",
        "AI , Tech 인사이트": "AIX", "신앙생활": "FTH", "스타트업 + 글로벌": "GLB"}

req = urllib.request.Request(RSS, headers={"User-Agent": "myblog-board"})
items = list(ET.fromstring(urllib.request.urlopen(req).read()).iter("item"))
count, latest = {}, {}
for it in items:
    c = (it.findtext("category") or "").strip()
    if c in CATS:
        count[c] = count.get(c, 0) + 1
        latest.setdefault(c, it)
newest = max(email.utils.parsedate_to_datetime(i.findtext("pubDate")) for i in latest.values())
rows = []
for c, it in sorted(latest.items(), key=lambda kv: email.utils.parsedate_to_datetime(kv[1].findtext("pubDate")), reverse=True):
    d = email.utils.parsedate_to_datetime(it.findtext("pubDate"))
    url = (it.findtext("link") or "").split("?")[0]
    title = re.sub(r"\s*#\S.*$", "", it.findtext("title").strip()).replace("&", "&amp;").replace("<", "&lt;")
    st = ("boarding", "탑승중") if (newest - d).days < 7 else ("ontime", "정시")
    dest = re.sub(r"\s*,\s*", " · ", c)
    rows.append(f'''              <tr class="row" data-href="{url}">
                <td class="flight">{CATS[c]} {count[c]:03d}</td><td class="dest">{dest}</td>
                <td class="post"><a href="{url}" target="_blank" rel="noopener">{title}</a></td>
                <td class="when">{d:%m.%d}</td><td class="status {st[0]}">{st[1]}</td>
              </tr>''')
html = INDEX.read_text(encoding="utf-8")
html = re.sub(r"(<tbody>\n).*?(\n\s*</tbody>)", lambda m: m[1] + "\n".join(rows) + m[2], html, count=1, flags=re.S)
INDEX.write_text(html, encoding="utf-8")
print(f"board: {len(rows)} rows")
