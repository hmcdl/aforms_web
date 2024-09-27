from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from app.secret_data import DATABASE_PASSWORD, DATABASE_NAME, DATABASE_PORT
from app.settings import SQLALCHEMY_DATABASE_URL

# SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:{DATABASE_PASSWORD}@localhost:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True
)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
