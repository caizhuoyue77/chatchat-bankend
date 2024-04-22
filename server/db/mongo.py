# db.py
from motor.motor_asyncio import AsyncIOMotorClient

# 全局变量，用于存储数据库客户端实例
db_client: AsyncIOMotorClient = None

def get_database_client() -> AsyncIOMotorClient:
    global db_client
    if db_client is None:
        db_client = AsyncIOMotorClient("mongodb://rootxyx:woxnsk!@localhost:27024/relation")
    return db_client

def get_database() -> AsyncIOMotorClient:
    return get_database_client().relation
