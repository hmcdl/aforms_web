from typing_extensions import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import update

from . import models
from . import schemas

from ..secret_data import ACCESS_TOKEN_EXPIRE_MINUTES
from ..users.users import Token, get_user_by_name, get_user_me, \
    oauth2_scheme, get_password_hash, verify_password, \
autorise, credentials_exception, create_access_token
from ..users import users
from ..database import Sessionlocal, get_db

router = APIRouter(prefix="/simulations", tags=["simulations"])

@router.post("/", response_model = schemas.Simulation)
def add_simulation(simulation: models.Simulation_default, token: Annotated[str, Depends(oauth2_scheme)],
                   db: Session = Depends(get_db), 
                   ):
    token_data = autorise(token=token)
    db_user = get_user_by_name(db, username=token_data.username)
    if db_user is None:
        raise credentials_exception
    if db_user.availible_simulations > 0:
        db_sim = models.Simulation_default(title=simulation.title, owner_id=db_user.id)
        db.add(db_sim)
        db_user.availible_simulations = db_user.availible_simulations - 1
        res = db.execute("select * from simulations")
        db.commit
        db.refresh(db_sim)
        return db_sim
        




