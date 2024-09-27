"""
Схемы отображения данных из таблицы проектов в джейсоны, возвращаемые АПИ
"""
from pydantic import BaseModel

class Simulation(BaseModel):
    """
    Данные, возвращаемые при запросе о проектах пользователя
    """
    id: int
    title : str
    owner_id : int
    class Config:
        orm_mode = True

class SimulationCreate(BaseModel):
    title : str

class conver_args(BaseModel):
    """
    Дефолтные аргументы запуска консольной AFORMS
    """
    iters: int = 1
    simulation: int = 1
    aeroratio: float = 1.5