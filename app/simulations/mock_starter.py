import os
import sys
import subprocess
from app.secret_data import simulation_executor
from os import path
from pathlib import Path

dir = r"c:\Work\Dev\simulations_web\sim_dir\tester"
abs_working_dir =   r"c:\Work\Dev\simulations_web\sim_dir\tester\job3"
# a = Path(__file__)
abs_working_dir = path.join(Path(__file__).absolute().parent(), abs_working_dir) 

title = "job3"
sp = subprocess.Popen(['python', simulation_executor, os.path.join(abs_working_dir, title)], cwd=abs_working_dir)
sp.wait()
print(sp.returncode)