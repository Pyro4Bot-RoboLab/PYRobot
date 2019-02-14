#!/usr/bin/env python3
import subprocess
try:
    subprocess.call(["pyclean", ".."])
except:
    print("error")
else:
    print("*.pyc borrados")
