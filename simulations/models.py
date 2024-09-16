from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, mapped_column

from ..database import Base
# from ..users.models import User
class Simulation(Base):
    __tablename__ = "simulations"
    id = mapped_column(Integer, primary_key=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)
    conver_args = Column(String, nullable=False)

    owner = relationship("User", back_populates="simulations")