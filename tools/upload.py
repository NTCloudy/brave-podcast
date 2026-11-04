"""Upload new/changed docs/audio/*.mp3 to the GitHub Release "audio" (Pages has a 1 GB site limit).

uploaded.json maps file -> mtime of the version that is on the release; build_feed.py only lists those.
"""
import glob, json, os, subprocess
REPO = "NTCloudy/brave-podcast"
TAG = "audio"
state = json.load(open("uploaded.json", encoding="utf-8")) if os.path.exists("uploaded.json") else {}
todo = [f for f in sorted(glob.glob("docs/audio/*.mp3"))
        if not f.endswith(".part.mp3") and state.get(os.path.basename(f)) != os.path.getmtime(f)]
for i in range(0, len(todo), 10):
    batch = todo[i:i + 10]
    subprocess.run(["gh", "release", "upload", TAG, *batch, "--clobber", "-R", REPO], check=True)
    for f in batch:
        state[os.path.basename(f)] = os.path.getmtime(f)
    json.dump(state, open("uploaded.json.tmp", "w", encoding="utf-8"), indent=0)
    os.replace("uploaded.json.tmp", "uploaded.json")
    print("uploaded", len(state), flush=True)
