"""네이버 블로그 RSS로 data/site.json 의 글 목록을 새로 쓴다. 화면(assets/app.js)은 이 파일을 읽어 그린다.

    python scripts/update_site.py

- 출발 안내판: 카테고리마다 최신 글 한 편 (편명 숫자 = 최근 글 중 그 카테고리 글 수)
- AI 인사이트: 최신 6편 (예전에 써 둔 한 줄 소개 'sub'는 같은 글이면 남긴다)
- 에세이 · 신앙생활 칸: 각각 최신 3편
- 여행 기록 사진 띠: 새 여행 글(달리기,여행,맛집)이 나오면 RSS 썸네일을 assets/blog/ 에 받아 맨 앞에 넣는다 (4장 유지)
- 최근 여정 · 책 연재처럼 손으로 고른 칸은 data/site.json 에서 직접 고친다
"""
import datetime, email.utils, json, re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

RSS = "https://rss.blog.naver.com/joekang.xml"
DATA = Path(__file__).resolve().parent.parent / "data/site.json"
CATS = {"달리기,여행,맛집": "TRV", "일상 생각,에세이": "ESY", "독서,책": "BKS",
        "AI , Tech 인사이트": "AIX", "신앙생활": "FTH", "스타트업 + 글로벌": "GLB"}

req = urllib.request.Request(RSS, headers={"User-Agent": "myblog-board"})
items = []
for it in ET.fromstring(urllib.request.urlopen(req, timeout=30).read()).iter("item"):
    items.append({"cat": (it.findtext("category") or "").strip(),
                  "url": (it.findtext("link") or "").split("?")[0],
                  "img": (re.findall(r'src=["\']([^"\']+)', it.findtext("description") or "") + [""])[0],
                  "title": re.sub(r"\s*#\S.*$", "", (it.findtext("title") or "").strip()),
                  "when": email.utils.parsedate_to_datetime(it.findtext("pubDate"))})
items.sort(key=lambda i: i["when"], reverse=True)
site = json.loads(DATA.read_text(encoding="utf-8"))
post = lambda i: {"url": i["url"], "title": i["title"], "date": f"{i['when']:%m.%d}"}  # noqa: E731

# 출발 안내판
count, latest = {}, {}
for i in items:
    if i["cat"] in CATS:
        count[i["cat"]] = count.get(i["cat"], 0) + 1
        latest.setdefault(i["cat"], i)
newest = max(i["when"] for i in latest.values())
site["board"]["rows"] = [{"code": f"{CATS[c]} {count[c]:03d}", "dest": re.sub(r"\s*,\s*", " · ", c), **post(i),
                          "status": "boarding" if (newest - i["when"]).days < 7 else "ontime"}
                         for c, i in sorted(latest.items(), key=lambda kv: kv[1]["when"], reverse=True)]
site["board"]["foot"] = f"편명 숫자 = 최근 글 {len(items)}편 중 해당 카테고리 글 수 · 행을 누르면 블로그 글로 이동합니다"

# 카테고리 칸
subs = {p["url"]: p.get("sub", "") for p in site["ai"]["posts"]}
site["ai"]["posts"] = [{**post(i), "sub": subs.get(i["url"], "")} for i in items if i["cat"] == site["ai"]["category"]][:6] or site["ai"]["posts"]
for col in site["columns"]:
    col["posts"] = [post(i) for i in items if i["cat"] == col["category"]][:3] or col["posts"]

# 여행 기록 사진 띠 — 나라 코드는 제목의 지명으로 어림한다 (모르면 KR)
CC = {"CN": "중국|베이징|상하이|상해|칭다오|웨이하이|다롄|대련|충칭|청두|시안|광저우|선전|홍콩", "MY": "말레이시아|쿠알라|페낭",
      "JP": "일본|도쿄|오사카|후쿠오카|교토", "VN": "베트남|하노이|다낭|호치민", "TH": "태국|방콕|치앙마이", "US": "미국|뉴욕|샌프란시스코",
      "TW": "대만|타이베이", "SG": "싱가포르", "PH": "필리핀|세부", "ID": "인도네시아|발리"}
strip = site["log"]["strip"]
last = max(int(s["url"].rsplit("/", 1)[-1]) for s in strip)  # 띠에 있는 가장 새 글보다 새 글만 (글 번호는 늘어나기만 한다)
for i in sorted((i for i in items if i["cat"] == "달리기,여행,맛집" and i["img"] and int(i["url"].rsplit("/", 1)[-1]) > last),
                key=lambda i: i["when"]):
    no = i["url"].rsplit("/", 1)[-1]
    try:
        img = urllib.request.urlopen(urllib.request.Request(i["img"], headers={
            "User-Agent": "Mozilla/5.0", "Referer": "https://blog.naver.com/"}), timeout=30).read()
    except Exception as e:
        print(f"  ! 썸네일 실패 {no}: {e}")
        continue
    (DATA.parent.parent / "assets/blog").mkdir(exist_ok=True)
    (DATA.parent.parent / f"assets/blog/{no}.jpg").write_bytes(img)
    cc = next((c for c, pat in CC.items() if re.search(pat, i["title"])), "KR")
    title = re.sub(r"^\[[^\]]*\]\s*", "", i["title"])
    strip.insert(0, {"url": i["url"], "src": f"assets/blog/{no}.jpg", "alt": title, "w": 773, "h": 580,
                     "title": title[:28], "meta": f"{cc} · {i['when']:%m.%d}"})
site["log"]["strip"] = strip[:4]

today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
site["updated"] = f"{today:%Y.%m.%d}"
site["footNote"] = re.sub(r"최근 \d+편, \d{4}\.\d{2}\.\d{2} 기준", f"최근 {len(items)}편, {site['updated']} 기준", site["footNote"])
DATA.write_text(json.dumps(site, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"site.json: 안내판 {len(site['board']['rows'])}줄 · AI {len(site['ai']['posts'])}편 · "
      + " · ".join(f"{c['label']} {len(c['posts'])}편" for c in site["columns"]) + f" · {site['updated']} 기준")
