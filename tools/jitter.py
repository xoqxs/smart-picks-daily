#!/usr/bin/env python3
"""Random wait so posts never go out at the same minute.

  python3 tools/jitter.py <key> <min_minutes> <max_minutes>

First call picks a random target time for <key> (stored in /tmp/jitter-<key>) and sleeps up to 9 minutes.
Call it again with the same arguments until it prints "done" (each Bash call stays under the 10-minute limit).
"""
import os, random, sys, time

key, lo, hi = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
path = f"/tmp/jitter-{key}"
if not os.path.exists(path):
    target = time.time() + random.uniform(lo, hi) * 60
    open(path, "w").write(str(target))
target = float(open(path).read())
left = target - time.time()
if left > 0:
    time.sleep(min(left, 540))
left = target - time.time()
if left <= 0:
    os.remove(path); print("done")
else:
    print(f"wait {left/60:.1f} more minutes")
