import os
import pathlib
import subprocess

from app.settings import (AFORMS_CONSOLE_PATH, NASTRAN_SOLVER_PATH,
                          PYTHON_PATH, OPTIMIZATION_SOLVER_PATH,
                          PANELCM, MATERIALS_DB)


def run_mock(arg) -> int:
    sp = subprocess.Popen(['python', "./app/drafts/simulation_mock.py"])
    sp.wait()
    return sp.returncode

def run_aformes(args_map: dict, cwd: str) -> int:
    optional_arguments_list = []
    for key in args_map:
        optional_arguments_list.append("--" + key)
        optional_arguments_list.append(str(args_map[key]))
    full_args_list = [AFORMS_CONSOLE_PATH,
                   "--solver", NASTRAN_SOLVER_PATH,
                   "--PythonPath", PYTHON_PATH,
                   "--optimizer_path", OPTIMIZATION_SOLVER_PATH,
                   "--panelcm", PANELCM,
                   "--materials", MATERIALS_DB,
                   *optional_arguments_list
                    ]
    print(" ".join(full_args_list))
    print(cwd)
    sp = subprocess.Popen(full_args_list, cwd=cwd)
    sp.wait()
    return sp.returncode
    # print(all_args)


def prepare_mdl(filename: str) -> None:
    """Замена зависимостей в mdl на локальные"""
    with open (filename, 'r') as f:
        lines = f.readlines()
        index_loads = [i for i in range(len(lines)) if lines[i].startswith("//loads")][0] + 2
        index_control_system = [i for i in range(len(lines)) if lines[i].startswith("//control_system")][0] + 2
        loads_path = pathlib.Path(lines[index_loads])
        loads_path = os.path.join(pathlib.Path(filename).parent, "AEROMANUAL.txt\n")
        control_system_path = pathlib.Path(lines[index_control_system])
        control_system_path = os.path.join(pathlib.Path(filename).parent, "control_system.json\n")
        lines[index_loads] = loads_path
        lines[index_control_system] = control_system_path
    with open(filename, 'w') as f:
        f.writelines(lines)



