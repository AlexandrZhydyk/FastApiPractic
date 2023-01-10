from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from pydantic import ValidationError, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED

from src.schemas.user import UserInDB, UserOut
from src.schemas.token import TokenRead
from src.db.models.users import User

# from src.db.base import db
from src.db.base import get_session
from src.core.config import Config
from datetime import datetime, timedelta

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth",
                                     scheme_name="JWT",
                                     scopes={"auth": "Access all info about current user",
                                             "company": "Access to create jobs",
                                             "superuser": "Access all info and actions",})


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


async def get_user(database, pk: int) -> UserInDB:
    query = select(User).where(User.id == pk)
    db_obj = await database.execute(query)
    instance = db_obj.scalar()
    return instance


async def get_user_by_email(database, email: str) -> UserInDB:
    query = select(User).where(User.email == email)
    db_obj = await database.execute(query)
    instance = db_obj.scalar()
    return instance


async def authenticate_user(database, email: str, password: str):
    user = await get_user_by_email(database, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=Config.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.JWT_REFRESH_SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_session),
                           ):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": 'authenticate_value'},
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        print(payload)
        # pk = payload.get("sub")
        email: EmailStr = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        print(token_scopes)
        token_data = TokenRead(scopes=token_scopes, email=email)
        print(token_data)
    except (JWTError, ValidationError):
        print("10")
        raise credentials_exception
    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        print("20")
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: UserOut = Security(get_current_user, scopes=["auth"])):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def check_company_credentials(user: UserOut = Security(get_current_active_user, scopes=["company"])) -> None:
    if not user.is_company:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="You are unauthorized")
    return user


async def check_superuser_credentials(user: UserOut = Security(get_current_active_user, scopes=["superuser"])) -> None:
    if not user.is_superuser:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="You are unauthorized")
    return user

