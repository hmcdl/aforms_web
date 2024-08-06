from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from ..simulations.models import Simulation_default

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    role_id = Column(Integer)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    availible_simulations = Column(Integer, default=5, nullable=False)

    simulations = relationship("Simulation_default", back_populates="owner")