# 토리아빠의 50플러스 인사이트

호기심 많은 중년 아재의 늦깎이 지구촌 탐구생활. 네이버 블로그 [blog.naver.com/joekang](https://blog.naver.com/joekang)의 개인 홈페이지입니다.

- 사이트: https://holyjoekang.github.io/myblog/
- 구성: `index.html`(화면 틀) + `assets/app.js`(그리기) + `data/site.json`(내용) + `assets/` 사진 — 빌드 도구 없음
- 동적 사이트: 화면은 열릴 때 `data/site.json`을 받아 그립니다. 로컬에서는 `python -m http.server`로 띄워 보세요.
- 글 목록(출발 안내판 · AI 인사이트 · 에세이 · 신앙생활)은 `python scripts/update_site.py`가 네이버 블로그 RSS로 새로 씁니다.
  `.github/workflows/update.yml`이 매일 아침 자동으로 돌립니다.
- 최근 여정 · 여행 기록 · 책 연재처럼 손으로 고른 칸은 `data/site.json`에서 직접 고칩니다.

관련 프로젝트: [나의 여행 지도](https://holyjoekang.github.io/my-travel-map/) · [나의 서재](https://holyjoekang.github.io/mybookshelf/) · [SafeFlock](https://holyjoekang.github.io/safeflock/)
