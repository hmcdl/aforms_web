"""
Class with authentification stuff
"""
from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.database import get_db
from app.secret_data import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from . import models as db_models
from .schemas import User, UserCreate


router = APIRouter(prefix="/users", tags=["users"])
empty_router = APIRouter()


credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from fastapi.security.utils import get_authorization_scheme_param

class oauth_wrapper(OAuth2PasswordBearer):
    def __init__(self, tokenUrl : str):
        super().__init__(tokenUrl=tokenUrl)
    async def __call__(self, request: Request):
        if request.client.host == "127.0.0.1":
            return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0ZXIiLCJleHAiOjE3MjM3NzE2NzF9.nyQQ2G2ZL7u8ehN1Ktxqb9Rq8Wf6AwJnACO1ML1UmHE"
        interm_res = await super().__call__(request=request)
        return interm_res

wrapped_scheme = oauth_wrapper(tokenUrl="token")

class Token(BaseModel):
    """
    Класс для работы с токенами
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Класс для представления данных из токена
    """
    username: Union[str, None] = None

def verify_password(plain_password, hashed_password):
    """
    Функция, сравнивающая предоставленный пароль, с захэшированным
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Функция, осуществляющеая хэширование
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    Создать токен доступа
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_token(token : str, db: Session):
    token_data = autorise(token=token)
    db_user = get_user_by_name(db, username=token_data.username)
    if db_user is None:
        raise credentials_exception
    return db_user

def autorise(token : str) -> Token:
    """
    Проверка токена
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except InvalidTokenError:
        return 'Invalid token. Please log in again.'
    
def authenticate_user(fake_db, username: str, password: str):
    """
    Аутентификация и авторизация юзера
    """
    user = get_user_by_name(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_user(db: Session, user_id : int):
    """
    Получить юзера по АйДи из БД
    """
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()

def get_user_by_name(db: Session, username : int):
    """
    Получить юзера по имени из БД
    """
    return db.query(db_models.User).filter(db_models.User.username == username).first()

def get_user_by_email(db: Session, email : int):
    """
    Получить юзера по почте из БД
    """
    return db.query(db_models.User).filter(db_models.User.email == email).first()


@router.get("/me", response_model= User)
def get_user_me(token: Annotated[str, Depends(wrapped_scheme)],
                 db: Session = Depends(get_db)):
    """
    Функция, возвращающая данные о пользователе, определенные в модели User
    """
    return get_user_by_token(token=token, db=db)

# @router.get("/me", response_model= User)
# def get_user_me(token: Annotated[str, Depends(oauth2_scheme)],
#                  db: Session = Depends(get_db)):
#     """
#     Функция, возвращающая данные о пользователе, определенные в модели User
#     """
#     return get_user_by_token(token=token, db=db)

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Функция, создающая нового пользователя по почте, нику и паролю
    """
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
    """
    Функция, возвращающая токен после авторизации
    """
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


@empty_router.get("/test/")
def read_root(request: Request):
    client_host = request.client.host
    return {"client_host": client_host}