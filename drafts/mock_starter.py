import os
import sys
import subprocess

dir = r"c:\Work\Dev\simulations_web\sim_dir\tester"
s = subprocess.Popen(["python", r"C:\Work\Dev\simulations_web\app\drafts\simulation_mock.py"], cwd=dir)
s.wait()
print(s.returncode)