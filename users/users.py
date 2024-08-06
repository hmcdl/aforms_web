"""
Class with authentification stuff
"""
from fastapi import APIRouter
from typing_extensions import Annotated
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from . import models as db_models
from .schemas import User, UserCreate
from app.secret_data import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.database import Sessionlocal, get_db

from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Union

from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])
empty_router = APIRouter()


credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )




class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def autorise(token : str) -> Token: 
    """
    return token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
def authenticate_user(fake_db, username: str, password: str):
    user = get_user_by_name(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_user(db: Session, user_id : int):
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()

def get_user_by_name(db: Session, username : int):
    return db.query(db_models.User).filter(db_models.User.username == username).first()

def get_user_by_email(db: Session, email : int):
    return db.query(db_models.User).filter(db_models.User.email == email).first()


@router.get("/me", response_model= User)
def get_user_me(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db) ):
    token_data = autorise(token=token)
    db_user = get_user_by_name(db, username=token_data.username)
    if db_user is None:
        raise credentials_exception
    return db_user

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)
    db_user = db_models.User(email=user.email, username=user.username, hashed_password=hashed_password, 
                             role_id=0, is_active=True, is_superuser=False, )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@empty_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
     db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")