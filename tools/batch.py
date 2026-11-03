"""學生會長是前世的勇者: brave/chNNN.txt -> docs/audio/eNNN.mp3; season = 集 (15 chapters each).

Chapter titles come from brave/titles.json. Skips existing audio;
regenerates when the chapter text is newer than its MP3. Updates episodes.json.
"""
import glob, json, os, re, subprocess, sys
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
BRAIN = os.path.expanduser("~/.gemini/jetski/brain/65a7a63d-68e1-4ec2-bbcc-730a51b2f9dd")
SRC = f"{BRAIN}/brave"
CN = "零一二三四五六七八九"
def cn(n):
    if n >= 100:  # 101 -> 一百零一, 115 -> 一百一十五, 120 -> 一百二十
        r = n % 100
        return CN[n // 100] + "百" + ("" if r == 0 else ("零" + CN[r] if r < 10 else (CN[1] + cn(r) if r < 20 else cn(r))))
    return CN[n] if n < 10 else ("十" + (CN[n % 10] if n % 10 else "") if n < 20 else CN[n // 10] + "十" + (CN[n % 10] if n % 10 else ""))
TITLES = {}
KT = f"{SRC}/titles.json"  # final chapter titles as published on KadoKado (preferred over the outline)
KTITLES = json.load(open(KT, encoding="utf-8")) if os.path.exists(KT) else {}
eps = json.load(open("episodes.json", encoding="utf-8")) if os.path.exists("episodes.json") else []
have = {e["file"] for e in eps}
base = datetime(2026, 11, 3, 12, tzinfo=timezone(timedelta(hours=8)))
for txt in sorted(glob.glob(f"{SRC}/ch[0-9][0-9][0-9].txt")):
    n = int(re.search(r"ch(\d+)\.txt", txt).group(1))
    if KTITLES and str(n) not in KTITLES:
        continue  # still being written: titles.json gets the title only once the volume is done
    season = (n - 1) // 15 + 1
    name = TITLES.get(n, "")
    title = KTITLES.get(str(n)) or (f"第{cn(n)}章　{name}" if name else f"第{cn(n)}章")
    f = f"e{n:03d}.mp3"
    mp3 = f"docs/audio/{f}"
    if os.path.exists(mp3) and os.path.getmtime(txt) > os.path.getmtime(mp3) + 60:
        os.remove(mp3)  # chapter text was edited after the audio was made: regenerate
    meta = {"title": f"前世勇者｜{title}", "summary": f"《學生會長是前世的勇者》第{cn(season)}集　{title}。"}
    old = next((e for e in eps if e["file"] == f), None)
    if old and old["title"] != meta["title"]:
        old.update(meta)  # chapter renamed: the spoken intro has the old title, so regenerate
        if os.path.exists(mp3): os.remove(mp3)
    if f in have and os.path.exists(mp3):
        continue
    if not os.path.exists(mp3):
        subprocess.run([sys.executable, "-u", "tools/tts.py", txt, mp3,
                        f"學生會長是前世的勇者。{title.replace('　', '，')}。", f"第{cn(n)}章，完。感謝收聽學生會長是前世的勇者。"], check=True)
    if f not in have:
        eps.append({"n": n, "season": season, "file": f, **meta,
                    "pub": format_datetime(base + timedelta(minutes=n))})
        have.add(f)
    json.dump(sorted(eps, key=lambda e: e["n"]), open("episodes.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("done", f, flush=True)
