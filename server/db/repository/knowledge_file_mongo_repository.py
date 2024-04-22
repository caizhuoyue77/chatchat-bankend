from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict
from mongo import get_database

# 列出某知识库某文件对应的所有Document
async def list_docs_from_db(kb_name: str, file_name: str = None, metadata: Dict = {}) -> List[Dict]:
    db = get_database()
    query = {"kb_name": kb_name}
    if file_name:
        query["file_name"] = file_name
    for k, v in metadata.items():
        query[f"metadata.{k}"] = str(v)
    
    docs = await db.kbfiles.find(query).to_list(None)
    return [{"id": doc["doc_id"], "metadata": doc["metadata"]} for doc in docs]

# 删除某知识库某文件对应的所有Document
async def delete_docs_from_db(kb_name: str, file_name: str = None) -> List[Dict]:
    db = get_database()
    docs = await list_docs_from_db(kb_name=kb_name, file_name=file_name)
    query = {"kb_name": kb_name}
    if file_name:
        query["file_name"] = file_name
    await db.kbfiles.delete_many(query)
    return docs

# 将Document信息添加到数据库
async def add_docs_to_db(kb_name: str, file_name: str, doc_infos: List[Dict]):
    db = get_database()
    if doc_infos is None:
        print("输入的doc_infos参数为None")
        return False

    for d in doc_infos:
        doc = {
            "kb_name": kb_name,
            "file_name": file_name,
            "doc_id": d["id"],
            "metadata": d["metadata"],
        }
        await db.kbfiles.insert_one(doc)
    return True

# 计算某知识库中的文件数量
async def count_files_from_db(kb_name: str) -> int:
    db = get_database()
    return await db.kbfiles.count_documents({"kb_name": kb_name})

# 列出某知识库中的所有文件
async def list_files_from_db(kb_name: str):
    db = get_database()
    files = await db.kbfiles.find({"kb_name": kb_name}).to_list(None)
    return [file["file_name"] for file in files]

# 将文件添加到数据库
async def add_file_to_db(kb_file, docs_count: int = 0, custom_docs: bool = False, doc_infos: List[str] = []):
    db = get_database()
    kb = await db.kbfiles.find_one({"kb_name": kb_file.kb_name})
    if kb:
        existing_file = await db.kbfiles.find_one({"file_name": kb_file.filename, "kb_name": kb_file.kb_name})
        mtime = kb_file.get_mtime()
        size = kb_file.get_size()

        if existing_file:
            await db.kbfiles.update_one(
                {"_id": existing_file["_id"]},
                {"$set": {"file_mtime": mtime, "file_size": size, "docs_count": docs_count, "custom_docs": custom_docs}}
            )
        else:
            new_file = {
                "file_name": kb_file.filename,
                "file_ext": kb_file.ext,
                "kb_name": kb_file.kb_name,
                # ... 其他字段
                "file_mtime": mtime,
                "file_size": size,
                "docs_count": docs_count,
                "custom_docs": custom_docs,
            }
            await db.kbfiles.insert_one(new_file)
            await db.kbfiles.update_one({"_id": kb["_id"]}, {"$inc": {"file_count": 1}})
        await add_docs_to_db(kb_name=kb_file.kb_name, file_name=kb_file.filename, doc_infos=doc_infos)
    return True

# 删除某知识库中的特定文件
async def delete_file_from_db(kb_file):
    db = get_database()
    existing_file = await db.kbfiles.find_one({"file_name": kb_file.filename, "kb_name": kb_file.kb_name})
    if existing_file:
        await db.kbfiles.delete_one({"_id": existing_file["_id"]})
        await delete_docs_from_db(kb_name=kb_file.kb_name, file_name=kb_file.filename)
        await db.kbfiles.update_one({"kb_name": kb_file.kb_name}, {"$inc": {"file_count": -1}})
    return True

# 删除某知识库中的所有文件
async def delete_files_from_db(knowledge_base_name: str):
    db = get_database()
    await db.kbfiles.delete_many({"kb_name": knowledge_base_name})
    await db.kbfiles.update_one({"kb_name": knowledge_base_name}, {"$set": {"file_count": 0}})
    return True

# 检查文件是否存在于数据库中
async def file_exists_in_db(kb_file):
    db = get_database()
    existing_file = await db.kbfiles.find_one({"file_name": kb_file.filename, "kb_name": kb_file.kb_name})
    return bool(existing_file)

# 获取文件详细信息
async def get_file_detail(kb_name: str, filename: str) -> dict:
    db = get_database()
    file = await db.kbfiles.find_one({"file_name": filename, "kb_name": kb_name})
    if file:
        return {k: file[k] for k in file if k != "_id"}
    else:
        return {}

# 请根据您的具体需求调整上述函数
