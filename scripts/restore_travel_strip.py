"""한 번만: 첫 자동 실행이 예전 여행 글로 덮어쓴 사진 띠를 손으로 고른 4장 + 새 공주 글로 되돌린다."""
import json, subprocess
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data/site.json"
site = json.loads(DATA.read_text(encoding="utf-8"))
old = json.loads(subprocess.run(["git", "show", "9068194:data/site.json"], capture_output=True, text=True,
                                cwd=DATA.parent, check=True).stdout)["log"]["strip"]
new = [s for s in site["log"]["strip"] if s["url"].endswith("224460326630")]
site["log"]["strip"] = (new + old)[:4]
DATA.write_text(json.dumps(site, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print([s["title"] for s in site["log"]["strip"]])
