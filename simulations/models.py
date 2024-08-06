from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base
# from ..users.models import User

class Simulation_default(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="simulations")