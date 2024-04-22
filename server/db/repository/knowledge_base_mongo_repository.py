from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB 连接设置
mongo_client = AsyncIOMotorClient('mongodb://localhost:27017')
database = mongo_client['your_database_name']  # 替换为您的数据库名称
collection = database['knowledge_bases']  # 替换为您的集合名称

# 添加或更新知识库
async def add_kb_to_db(kb_name, kb_info, vs_type, embed_model):
    kb = await collection.find_one({"kb_name": kb_name})
    if not kb:
        await collection.insert_one({
            "kb_name": kb_name, 
            "kb_info": kb_info, 
            "vs_type": vs_type, 
            "embed_model": embed_model
        })
    else:
        await collection.update_one(
            {"kb_name": kb_name}, 
            {"$set": {
                "kb_info": kb_info, 
                "vs_type": vs_type, 
                "embed_model": embed_model
            }}
        )
    return True

# 列出知识库
async def list_kbs_from_db(min_file_count: int = -1):
    kbs = await collection.find(
        {"file_count": {"$gt": min_file_count}}, 
        {"kb_name": 1}
    ).to_list(None)
    return [kb["kb_name"] for kb in kbs]

# 检查知识库是否存在
async def kb_exists(kb_name):
    kb = await collection.find_one({"kb_name": kb_name})
    return bool(kb)

# 从数据库加载知识库
async def load_kb_from_db(kb_name):
    kb = await collection.find_one({"kb_name": kb_name})
    if kb:
        return kb['kb_name'], kb['vs_type'], kb['embed_model']
    else:
        return None, None, None

# 删除知识库
async def delete_kb_from_db(kb_name):
    await collection.delete_one({"kb_name": kb_name})
    return True

# 获取知识库详情
async def get_kb_detail(kb_name: str) -> dict:
    kb = await collection.find_one({"kb_name": kb_name})
    if kb:
        return {
            "kb_name": kb.get("kb_name"),
            "kb_info": kb.get("kb_info"),
            "vs_type": kb.get("vs_type"),
            "embed_model": kb.get("embed_model"),
            "file_count": kb.get("file_count"),
            "create_time": kb.get("create_time"),
        }
    else:
        return {}

# 请根据您的具体需求调整上述函数
