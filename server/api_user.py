from server.db.mongo import get_database
from server.utils import (BaseResponse, ListResponse, FastAPI, MakeFastAPIOffline,
                          get_server_configs, get_prompt_template)
from pydantic import BaseModel
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError


# 用户注册模型
class UserRegister(BaseModel):
    username: str
    password: str


# 用户登录模型
class UserLogin(BaseModel):
    username: str
    password: str


# 初始化密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 令牌的秘钥和算法
SECRET_KEY = "your_secret_key"  # 替换为你的秘钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 令牌有效期


# 散列密码
def hash_password(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


def mount_user_routes(app: FastAPI):
    @app.post("/register")
    async def register(user: UserRegister):
        db = get_database()
        # 检查用户是否已存在
        if await db.users.find_one({"username": user.username}):
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = hash_password(user.password)
        user_dict = user.dict()
        user_dict.update({"password": hashed_password})  # 更新为散列后的密码
        await db.users.insert_one(user_dict)
        return {"message": "User registered successfully"}

    @app.post("/login")
    async def login(user: UserLogin):
        db = get_database()
        db_user = await db.users.find_one({"username": user.username})
        if not db_user or not pwd_context.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}

    @app.get("/users/me")
    async def read_users_me(current_user: dict = Depends(get_current_user)):
        return current_user
