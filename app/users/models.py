"""
Классовое представление пользователя из базы данных
"""
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship, mapped_column

from app.database import Base

class User(Base):
    """
    Класс, представляющий сущность пользователя для орм-ки
    """
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    role_id = Column(Integer)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    availible_simulations = Column(Integer, default=100000, nullable=False)

    simulations = relationship("Simulation", back_populates="owner")
    