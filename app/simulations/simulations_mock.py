import sys
import pathlib
import os
print ('starting simulation mock')
args = sys.argv[1:]

working_dir = pathlib.Path(args[0]).parent

with open (args[0], 'r') as f:
    content = f.read()
    print(content)

with open (os.path.join(working_dir, "results.txt"), 'w') as f:
    f.write("results of simulation mock")
print('simulation mock finished')