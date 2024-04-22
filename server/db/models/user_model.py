from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    password: str


# 用户登录模型
class UserLogin(BaseModel):
    username: str
    password: str
