from sqlalchemy import create_engine, select

from sqlalchemy.orm import declarative_base, sessionmaker
from app.users.models import User
from app.simulations.models import Simulation

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:88495@localhost:5432/test_db"

engine = create_engine(url=SQLALCHEMY_DATABASE_URL, echo=True)
Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = Sessionlocal()
usr = session.get(User, 1)
print(usr.username)

# for user in session.scalars(stmt):
#     print(user)