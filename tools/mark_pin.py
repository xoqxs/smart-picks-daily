#!/usr/bin/env python3
"""Mark one pins.json entry as posted and push right away (so parallel runs don't repin it).
  python3 tools/mark_pin.py <pins.json index> <pin url>
"""
import json, subprocess, sys, datetime, zoneinfo, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
subprocess.run(["git", "pull", "-q", "--rebase"], check=True)
i, url = int(sys.argv[1]), sys.argv[2]
q = json.load(open("pins.json"))
today = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Istanbul")).date().isoformat()
if q[i]["posted"]:
    print("ALREADY POSTED", q[i]["posted"], q[i]["pin_url"]); sys.exit(1)
q[i]["posted"], q[i]["pin_url"] = today, url
json.dump(q, open("pins.json", "w"), indent=1, ensure_ascii=False)
subprocess.run(["git", "-c", "user.name=Smart Picks Daily", "-c", "user.email=noreply@anthropic.com", "commit", "-qam",
                f"Pin posted: pick {q[i]['pick']}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], check=True)
for _ in range(3):
    if subprocess.run(["git", "-c", "push.negotiate=true", "push", "-q", "origin", "HEAD:main"]).returncode == 0: break
    subprocess.run(["git", "pull", "-q", "--rebase"])
print("marked", i, q[i]["pick"], url)
