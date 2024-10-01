"""
Реализация эндпойнтов, связанных с симуляциями
"""
import json
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
from . import util

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
    abs_working_dir = os.path.join(SIMULATIONS_DIR, relational_working_dir, title)
    if not os.path.isdir(os.path.join(SIMULATIONS_DIR, relational_working_dir)):
        os.mkdir(os.path.join(SIMULATIONS_DIR, relational_working_dir))
    if not os.path.isdir(abs_working_dir):
        os.mkdir(abs_working_dir)
    else:
        raise HTTPException(status_code=200, detail=f"title {title} already exists")
    
    # загружаем файлы на сервер. 
    # Добавить исключения по ошибкам типа отсутствия памяти на диске? Хотя эти файлы все легкие...
    try:
        util.upload_file(abs_working_dir, title + ".mdl3", mdl)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fail while writing to file") from exc

    try:
        util.upload_file(abs_working_dir, "AEROMANUAL.txt", aeromanual)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fail while writing to file") from exc
    
    try:
        util.upload_file(abs_working_dir, "from_interface.json", from_interface)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fail while writing to file") from exc
    
    try:
        util.upload_file(abs_working_dir, "control_system.json", control_system)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Fail while writing to file") from exc

    # Создаем проект в бд и завершаем транзакцию
    try:
        db_sim = models.Simulation(title=title, owner_id=db_user.id,
                               status="not_calculated", created=datetime.now(),
                               conver_args="not set")
        db.add(db_sim)
        db.commit()
    except Exception as transaction_exception: # sqlalchemy.exc.ProgrammingError ?
        # Если ловим ошибку на этапе записи в БД удаляем директорию с симуляцией
        rmtree(abs_working_dir)
        db.rollback()
        raise transaction_exception
    
    return db_sim

@router.post("/remove_sim")
def remove_sim(title: str, token: Annotated[str, Depends(oauth2_scheme)],
               db: Session = Depends(get_db)):
    """Удаление проекта из БД"""
    db_user = get_user_by_token(token=token, db=db)
    relational_working_dir = db_user.username
    abs_user_dir = os.path.join(SIMULATIONS_DIR, relational_working_dir)
    abs_working_dir = os.path.join(abs_user_dir, title)
    if not os.path.isdir(abs_working_dir):
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    try:
        db.delete(db.query(models.Simulation).filter(models.Simulation.title==title).first())
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    rmtree(abs_working_dir)
    if len(abs_user_dir) == 0:
        rmtree(abs_user_dir)
    
    return {"status_code": 200, "detail": f"title {title} successfully removed"}


@router.get("/show_my_sims", response_model=List[schemas.Simulation])
def show_my_sims(token: Annotated[str, Depends(oauth2_scheme)], 
                 db: Session = Depends(get_db), limit : int = 100, offset : int = 0 ):
    """Показать все проекты юзера"""
    print("log")
    db_user = get_user_by_token(token=token, db=db)
    try:
        q = db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id).all()
    except Exception:
        return {"status_code": 500, "detail": ""} 
    projects_slice : List[models.Simulation] = q[offset:][:limit]
    return projects_slice

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

    title_quantity = len(db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id, 
                                              models.Simulation.title==title).all())
    if title_quantity == 0:
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    
    relational_user_dir = db_user.username
    # полный путь к папке с проектом
    abs_working_dir = os.path.join(SIMULATIONS_DIR, relational_user_dir, title)
    conver_args = json.loads(conver_args.model_dump_json())
    # название модели в аргументах запуска aforms должно быть с обратными слэшами, просто потому что
    conver_args["model"] =  os.path.join(abs_working_dir, title + ".mdl3").replace("/", "\\")
    # замена зависимостей в файле модели на локальные
    try:
        run_aformes.prepare_mdl(os.path.join(abs_working_dir, title + ".mdl3"))
    except IndexError:
        raise HTTPException(status_code=406, detail=f"Problem with .mdl3 content")
    log_file_path = os.path.join(abs_working_dir,"ConverLog00000.log")
    # создаем лог-файл в директории проекта
    with open(log_file_path, 'w') as f:
        pass
    log_socket_abs_path = os.path.abspath(os.path.join(Path(__file__).parent, "log_socket.py") )
    # print(f"{log_socket_abs_path} {request.client.host} 60606 {log_file_path}")
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
    abs_working_dir = os.path.join(SIMULATIONS_DIR, relational_working_dir, title)
    archieve_filename = abs_working_dir
    root_dir = os.path.join(SIMULATIONS_DIR, relational_working_dir, title)
    make_archive(base_name=archieve_filename, format='zip', root_dir=root_dir)
    
    return FileResponse(archieve_filename + ".zip", filename='results.zip', media_type='multipart/form-data')
