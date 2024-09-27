import os
import subprocess
import sys
sys.path.append(os.getcwd())
print(sys.path)
# from app.globals import deps
# str = """
# c:/Production/Console.exe --solver \"c:/Program Files/Siemens/FEMAPv1142/nastran/bin/nastran.exe\" --PythonPath \"c:/Users/Mikhail/AppData/Local/Programs/Python/Python310/python.exe\" --optimizer_path \"c:/Production/panel_optimizer\" --panelcm \"c:/Production/Buckling\" --materials \"c:/Production/Materials.txt\" --iters 1 --simulation 1 --aeroratio 1.5 --model \"c:/Work/Dev/simulations_web/sim_dir/tester/job8/job8.mdl3\"
# """
# print(str)
cwd = "c:/Work/Dev/simulations_web/sim_dir/tester/job8"
args_map = {"iters": 1, "simulation": 0, "aeroratio": 1.5}
optional_arguments_list = []
for key in args_map:
        optional_arguments_list.append("--" + key)
        optional_arguments_list.append(str(args_map[key]))
full_args_list = [deps["console_path"],
                   "--solver", deps["solver"] + "\"",
                   "--PythonPath",deps["PythonPath"] + "\"",
                   "--optimizer_path", "\"" + deps["optimizer_path"] + "\"",
                   "--panelcm", "\"" + deps["panelcm"] + "\"",
                   "--materials", "\"" + deps["materials"] + "\"",
                   *optional_arguments_list
                    ]
sp = subprocess.Popen(full_args_list, cwd=cwd)
sp.wait()
print(sp.returncode)

# args_list = [
#     "c:/Production/Console.exe",
#     "--solver", "c:/Program Files/Siemens/FEMAPv1142/nastran/bin/nastran.exe",
#     "--model", "c:\\Work\\Dev\\simulations_web\\sim_dir\\tester\\job8\\job8.mdl3",
#     "--PythonPath", "c:/Users/Mikhail/AppData/Local/Programs/Python/Python310/python.exe",
#     "--optimizer_path", "c:/Production/panel_optimizer",
#     "--panelcm", "c:/Production/Buckling",
#     "--materials", "c:/Production/Materials.txt",
#     "--iters", "1",
#     "--simulation", "0",
#     "--aeroratio", "1.5"
# ]
# args_list_str = " ".join(args_list)
# cwd = "c:/Work/Dev/simulations_web/sim_dir/tester/job8"
# with open(os.path.join(cwd, 'command3.bat'), 'w') as f:
#     f.write(" ".join(args_list))
# print(" ".join(args_list))
# # sp = subprocess.Popen(args=args_list[1:], executable=args_list[0], cwd=cwd)
# # sp = subprocess.Popen()
# sp = subprocess.run(args=args_list, cwd=cwd)
# # sp.wait()
# print(sp.returncode)