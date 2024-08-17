"""
Схемы отображения объектов из сущности юзеров в БД в джейсоны, возвращаемые АПИ
"""
from pydantic import BaseModel

class UserBase(BaseModel):
    """
    Родительский класс
    """
    email: str
    username: str

class UserCreate(UserBase):
    """
    Модель возврата при создании нового юзера
    """
    password: str

class User(UserBase):
    """
    Модель возврата при запросе информации о себе от авторизованного юзера
    """
    id: int
    is_active: bool
    role_id: int
    is_superuser: bool
    availible_simulations: int

    class Config:
        """
        Что=то вспомогательное для орм-ки
        """
        orm_mode = True