import subprocess

from local_depends_data import deps

def run_aformes(args_map: dict, cwd: str) -> int:
    optional_arguments_list = []
    for key in args_map:
        optional_arguments_list.append(key)
        optional_arguments_list.append(str(args_map[key]))
    sp = subprocess.Popen([deps["console_path"],
                   "--solver", deps["solver"],
                   "--PythonPath", deps["PythonPath"],
                   "--optimizer_path", deps["optimizer_path"],
                   "--panelcm", deps["panelcm"],
                   "--materials", deps["materials"],
                   "--model", deps["model"],
                   *optional_arguments_list
                    ], cwd=cwd)
    sp.wait()
    print(sp.returncode)
    # print(all_args)

# run_aformes({"--simulation": 0, "--iters": 0}, cwd="c:/Work/Dev/simulations_web/sim_dir/tester/LMS19")



