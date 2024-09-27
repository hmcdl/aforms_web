import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_PORT = os.environ.get("DATABASE_PORT")
SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
SIMULATIONS_DIR = os.environ.get("SIMULATIONS_DIR")

AFORMS_CONSOLE_PATH = os.environ.get("AFORMS_CONSOLE_PATH")
NASTRAN_SOLVER_PATH = os.environ.get("NASTRAN_SOLVER_PATH")
PYTHON_PATH = os.environ.get("PYTHON_PATH")
OPTIMIZATION_SOLVER_PATH = os.environ.get("OPTIMIZATION_SOLVER_PATH")
PANELCM = os.environ.get("PANELCM")
MATERIALS_DB = os.environ.get("MATERIALS_DB")

