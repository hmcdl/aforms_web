"""
Реализация эндпойнтов, связанных с симуляциями
"""
from os import mkdir, path, listdir
from datetime import datetime
from shutil import rmtree
from typing import List

from typing_extensions import Annotated
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.globals import sim_dir
from . import models
from . import schemas
from ..users.users import oauth2_scheme, get_user_by_token
from ..database import get_db

router = APIRouter(prefix="/simulations", tags=["simulations"])

@router.post("/", response_model = schemas.Simulation)
def add_simulation(token: Annotated[str, Depends(oauth2_scheme)],
                   mdl: UploadFile,
                   conver_args_string: str,
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
        with open(path.join(abs_working_dir, title), 'wb+') as f:
            contents = mdl.file.read()
            f.write(contents)
    except Exception: #Какую ошибку можно выкатить?
        raise HTTPException(status_code=500, detail=f"Fail while writing to file")
    try:
        db_sim = models.Simulation(title=title, owner_id=-1,
                               status="not_calculated", created=datetime.now(),
                               conver_args=conver_args_string)
        db.add(db_sim)
        db.commit()
    except Exception as e: # sqlalchemy.exc.ProgrammingError ?
        # Если ловим ошибку на этапе записи в БД удаляем директорию с симуляцией
        rmtree(abs_working_dir)    
        raise e
    return db_sim

@router.post("/remove_sim/")
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

@router.get("/show_my_sims/", response_model=List[schemas.Simulation])
def show_my_sims(token: Annotated[str, Depends(oauth2_scheme)], 
                 db: Session = Depends(get_db), limit : int = 100, offset : int = 0 ):
    """Показать все расчеты юзера"""
    db_user = get_user_by_token(token=token, db=db)
    q = db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id).all()
    return q[offset:][:limit]

@router.post("/start_simulation")
def start_simulation(title : str, token : Annotated[str, Depends(oauth2_scheme)],
                     db: Session = Depends(get_db),
                     ):
    """Запустить расчет. Пока расчет в виде заглушки"""
    db_user = get_user_by_token(token=token, db=db)
    if len(db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id, 
                                              models.Simulation.title==title).all()) == 0:
        raise HTTPException(status_code=200, detail=f"title {title} doesnt exists")
    relational_working_dir = db_user.username
    abs_working_dir = path.join(sim_dir, relational_working_dir, title)
    with open(path.join(abs_working_dir, "kind_of_results.txt"), 'w') as f:
        f.write("some results")
    db.query(models.Simulation).filter(models.Simulation.owner_id==db_user.id,
                                              models.Simulation.title==title).first().status = "calculated"
    db.commit()
    return {"status_code": 200, "detail": "simulation finished successfully"}

