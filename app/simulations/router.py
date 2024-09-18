"""
Реализация эндпойнтов, связанных с симуляциями
"""
import json
from os import mkdir, path, listdir
import os
from pathlib import Path
from datetime import datetime
from shutil import rmtree, make_archive
import time
from typing import List
import subprocess
# import zlib

from typing_extensions import Annotated
from fastapi import APIRouter, Depends, UploadFile, HTTPException, Request, Form
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.globals import sim_dir
from app.simulations import log_socket
from . import models
from . import schemas
from ..users.users import oauth2_scheme, get_user_by_token
from ..database import get_db
# from app.globals import simulation_executor
from . import run_aformes

router = APIRouter(prefix="/simulations", tags=["simulations"])

@router.post("/add_simulation", response_model = schemas.Simulation)
def add_simulation(token: Annotated[str, Depends(oauth2_scheme)],
                mdl: UploadFile,
                aeromanual: UploadFile,
                from_interface: UploadFile,
                control_system: UploadFile,
                # conver_args_string: str,
                title: str,
                db: Session = Depends(get_db)
                   ):
    """
    Add sumilation to user
    """
    db_user = get_user_by_token(token=token, db=db)
    relational_working_dir = db_user.username
    abs_working_dir = path.join(sim_dir, relational_working_dir, title)
    if not path.isdir(path.join(sim_dir, relational_working_dir)):
        mkdir(path.join(sim_dir, relational_working_dir))
    if not path.isdir(abs_working_dir):
        mkdir(abs_working_dir)
    else:
        raise HTTPException(status_code=200, detail=f"title {title} already exists")
    try:
        with open(path.join(abs_working_dir, title + ".mdl3"), 'wb+') as f:
            contents = mdl.file.read()
            f.write(contents)
    except Exception: #Какую ошибку можно выкатить?
        raise HTTPException(status_code=500, detail=f"Fail while writing to file")
    try:
        with open(path.join(abs_working_dir, "AEROMANUAL.txt"), 'wb+') as f:
            contents = aeromanual.file.read()
            f.write(contents)
    except Exception: #Какую ошибку можно выкатить?
        raise HTTPException(status_code=500, detail=f"Fail while writing to file")
    try:
        with open(path.join(abs_working_dir, "from_interface.json"), 'wb+') as f:
            contents = from_interface.file.read()
            f.write(contents)
    except Exception: #Какую ошибку можно выкатить?
        raise HTTPException(status_code=500, detail=f"Fail while writing to file")
    try:
        with open(path.join(abs_working_dir, "control_system.json"), 'wb+') as f:
            contents = control_system.file.read()
            f.write(contents)
    except Exception: #Какую ошибку можно выкатить?
        raise HTTPException(status_code=500, detail=f"Fail while writing to file")
    
    try:
        db_sim = models.Simulation(title=title, owner_id=db_user.id,
                               status="not_calculated", created=datetime.now(),
                               conver_args="not set")
        db.add(db_sim)
        db.commit()
    except Exception as e: # sqlalchemy.exc.ProgrammingError ?
        # Если ловим ошибку на этапе записи в БД удаляем директорию с симуляцией
        rmtree(abs_working_dir)    
        raise e
    return db_sim

@router.post("/remove_sim")
def remove_sim(title: str, token: Annotated[str, Depends(oauth2_scheme)],
               db: Session = Depends(get_db)):
    """Удаление симуляции из БД"""
    db_user = get_user_by_token(token=token, db=db)
    relational_working_dir = db_user.username
    abs_working_dir = path.join(sim_dir, relational_working_dir, title)
    if not path.isdir(abs_working_dir):
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    try:
        db.delete(db.query(models.Simulation).filter(models.Simulation.title==title).first())
        db.commit()
    except Exception as e:
        raise e
    rmtree(abs_working_dir)
    if len(listdir(path.join(sim_dir, relational_working_dir))) == 0:
        rmtree(path.join(sim_dir, relational_working_dir))
    return {"status_code": 200, "detail": f"title {title} successfully removed"}


@router.get("/show_my_sims", response_model=List[schemas.Simulation])
def show_my_sims(token: Annotated[str, Depends(oauth2_scheme)], 
                 db: Session = Depends(get_db), limit : int = 100, offset : int = 0 ):
    """Показать все расчеты юзера"""
    print("log")
    db_user = get_user_by_token(token=token, db=db)
    q = db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id).all()
    return q[offset:][:limit]

@router.post("/start_simulation")
def start_simulation(request : Request,
                    title : str,
                    conver_args: schemas.conver_args,
                    token : Annotated[str, Depends(oauth2_scheme)],
                    db: Session = Depends(get_db),
                     
                     ):
    """Запустить расчет"""
    db_user = get_user_by_token(token=token, db=db)
    if len(db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id, 
                                              models.Simulation.title==title).all()) == 0:
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    relational_working_dir = db_user.username
    # название папки с симуляцией
    abs_working_dir = path.join(sim_dir, relational_working_dir, title)
    # abs_working_dir = path.join(Path(__file__).absolute().parent, abs_working_dir) 
    # sp = subprocess.Popen(['python', simulation_executor, path.join(abs_working_dir, title)], cwd=abs_working_dir)
    conver_args = json.loads(conver_args.model_dump_json())
    conver_args["model"] =  path.join(abs_working_dir, title + ".mdl3").replace("/", "\\")
    run_aformes.prepare_mdl(path.join(abs_working_dir, title + ".mdl3"))
    log_file_path = path.join(abs_working_dir,"ConverLog00000.log")
    with open(log_file_path, 'w') as f:
        pass
    # log_socket.transmit_log(host=request.client.host, port=60606,
    #                          log_file_path=log_file_path)
    
    log_socket_abs_path = os.path.abspath(os.path.join(Path(__file__).parent, "log_socket.py") )
    print(f"{log_socket_abs_path} {request.client.host} 60606 {log_file_path}")
                    #  {request.client.host} 60606 {log_file_path}")
    subprocess.Popen(f'python {log_socket_abs_path} {request.client.host} 60606 {log_file_path}')
    returncode = run_aformes.run_aformes(args_map=conver_args, cwd=abs_working_dir)
    # sp.wait()
    if returncode == 0:
        db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id,
                                                models.Simulation.title==title).first().status = "calculated"
        db.commit()
        return {"status_code": 200, "detail": "simulation finished successfully"}
    else:
        return {"status_code": 400, "detail": f"simulation finished with returncode {returncode}"}

@router.get("/download")
def download_sim(title: str, token : Annotated[str, Depends(oauth2_scheme)],
                     db: Session = Depends(get_db),):
    db_user = get_user_by_token(token=token, db=db)
    # return FileResponse(path='data.xlsx', filename='Статистика покупок.xlsx', media_type='multipart/form-data')
    if len(db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id, 
                                              models.Simulation.title==title).all()) == 0:
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    relational_working_dir = db_user.username
    abs_working_dir = path.join(sim_dir, relational_working_dir, title)
    archieve_filename = abs_working_dir
    root_dir = path.join(sim_dir, relational_working_dir, title)
    make_archive(base_name=archieve_filename, format='zip', root_dir=root_dir)
    return FileResponse(archieve_filename + ".zip", filename='results.zip', media_type='multipart/form-data')

@router.get("/ip_echo")
def ip_echo(request: Request):
    return({"ip": request.client.host})