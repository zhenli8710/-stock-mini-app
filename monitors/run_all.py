import os, subprocess, sys
base = os.path.dirname(__file__)
for m in ["monitor_price.py","monitor_jobs.py","monitor_content.py"]:
    print(f"=== {m} ===")
    subprocess.run([sys.executable, os.path.join(base, m)], cwd=base)
