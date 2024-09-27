"""
Реализация эндпойнтов, связанных с симуляциями
"""
import json
from os import mkdir, path, listdir
import os
from pathlib import Path
from datetime import datetime
from shutil import rmtree, make_archive
from typing import List
import subprocess

from typing_extensions import Annotated
from fastapi import APIRouter, Depends, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.settings import SIMULATIONS_DIR
from . import models
from . import schemas
from ..users.router import oauth2_scheme, get_user_by_token
from ..database import get_db
from . import run_aformes

router = APIRouter(prefix="/simulations", tags=["simulations"])

@router.post("/add_simulation", response_model = schemas.Simulation)
def add_simulation(token: Annotated[str, Depends(oauth2_scheme)],
                mdl: UploadFile,
                aeromanual: UploadFile,
                from_interface: UploadFile,
                control_system: UploadFile,
                title: str,
                db: Session = Depends(get_db)
                   ):
    """
    Добавляем проект с уникальным названием title
    Основной файл модели - mdl, остальные - необходимые вспомогательные файлы для расчета
    Хранение данных устроено таким образом, что в базе данных хранится информация о проектах,
    а сами проекты хранятся на диске. 
    """
    db_user = get_user_by_token(token=token, db=db)
    relational_working_dir = db_user.username
    abs_working_dir = path.join(SIMULATIONS_DIR, relational_working_dir, title)
    if not path.isdir(path.join(SIMULATIONS_DIR, relational_working_dir)):
        mkdir(path.join(SIMULATIONS_DIR, relational_working_dir))
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
        db.rollback() 
        raise e
    return db_sim

@router.post("/remove_sim")
def remove_sim(title: str, token: Annotated[str, Depends(oauth2_scheme)],
               db: Session = Depends(get_db)):
    """Удаление проекта из БД"""
    db_user = get_user_by_token(token=token, db=db)
    relational_working_dir = db_user.username
    abs_working_dir = path.join(SIMULATIONS_DIR, relational_working_dir, title)
    if not path.isdir(abs_working_dir):
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    try:
        db.delete(db.query(models.Simulation).filter(models.Simulation.title==title).first())
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    rmtree(abs_working_dir)
    if len(listdir(path.join(SIMULATIONS_DIR, relational_working_dir))) == 0:
        rmtree(path.join(SIMULATIONS_DIR, relational_working_dir))
    return {"status_code": 200, "detail": f"title {title} successfully removed"}


@router.get("/show_my_sims", response_model=List[schemas.Simulation])
def show_my_sims(token: Annotated[str, Depends(oauth2_scheme)], 
                 db: Session = Depends(get_db), limit : int = 100, offset : int = 0 ):
    """Показать все проекты юзера"""
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
    """Запустить расчет проекта с названием title
    Аргументы запуска передаются в виде джейсона conver_args
    Перехват запроса request необходим, чтобы подключиться к сокету
    клиентского приложения для передачи логов о ходе выполнения расчета
    """
    db_user = get_user_by_token(token=token, db=db)
    if len(db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id, 
                                              models.Simulation.title==title).all()) == 0:
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    relational_working_dir = db_user.username
    # полный путь к папке с проектом
    abs_working_dir = path.join(SIMULATIONS_DIR, relational_working_dir, title)
    conver_args = json.loads(conver_args.model_dump_json())
    # название модели в аргументах запуска aforms должно быть с обратными слэшами, просто потому что
    conver_args["model"] =  path.join(abs_working_dir, title + ".mdl3").replace("/", "\\")
    # замена зависимостей в файле модели на локальные
    run_aformes.prepare_mdl(path.join(abs_working_dir, title + ".mdl3"))
    log_file_path = path.join(abs_working_dir,"ConverLog00000.log")
    # создаем лог-файл в директории проекта
    with open(log_file_path, 'r') as f:
        pass
    log_socket_abs_path = os.path.abspath(os.path.join(Path(__file__).parent, "log_socket.py") )
    print(f"{log_socket_abs_path} {request.client.host} 60606 {log_file_path}")
    # Запускаем сокет на оптправку логов
    subprocess.Popen(f'python {log_socket_abs_path} {request.client.host} 60606 {log_file_path}')
    # Запускаем расчет проекта
    returncode = run_aformes.run_aformes(args_map=conver_args, cwd=abs_working_dir)
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
    """
    Загружаем проект обратно на локальную машину
    !!!Добавить фильтр по загружаемым файлам, чтобы не качать гигабайты
    """
    db_user = get_user_by_token(token=token, db=db)
    if len(db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id, 
                                              models.Simulation.title==title).all()) == 0:
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    relational_working_dir = db_user.username
    abs_working_dir = path.join(SIMULATIONS_DIR, relational_working_dir, title)
    archieve_filename = abs_working_dir
    root_dir = path.join(SIMULATIONS_DIR, relational_working_dir, title)
    make_archive(base_name=archieve_filename, format='zip', root_dir=root_dir)
    return FileResponse(archieve_filename + ".zip", filename='results.zip', media_type='multipart/form-data')
