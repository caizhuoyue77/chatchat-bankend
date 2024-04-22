import urllib
from server.api_user import get_current_user
from server.utils import BaseResponse, ListResponse
from server.knowledge_base.utils import validate_kb_name
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.db.repository.knowledge_base_repository import list_kbs_from_db
from configs import EMBEDDING_MODEL, logger, log_verbose
from fastapi import Body, Depends, Form
from pydantic import Json
import json
from openapi_spec_validator import validate_spec
import os


# def list_kbs(current_user: dict = Depends(get_current_user)):
#     # Get List of Knowledge Base
#     user_id = current_user.get("username")
#     kbs_list = list_kbs_from_db()
#     return ListResponse(data=kbs_list)
def list_kbs():
    # Get List of Knowledge Base
    kbs_list = list_kbs_from_db()
    return ListResponse(data=kbs_list)

def create_kb(knowledge_base_name: str = Body(..., examples=["samples"]),
            vector_store_type: str = Body("faiss"),
            embed_model: str = Body(EMBEDDING_MODEL),
            ) -> BaseResponse:
    # Create selected knowledge base
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")
    if knowledge_base_name is None or knowledge_base_name.strip() == "":
        return BaseResponse(code=404, msg="知识库名称不能为空，请重新填写知识库名称")

    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is not None:
        return BaseResponse(code=404, msg=f"已存在同名知识库 {knowledge_base_name}")

    kb = KBServiceFactory.get_service(knowledge_base_name, vector_store_type, embed_model)
    try:
        kb.create_kb()
    except Exception as e:
        msg = f"创建知识库出错： {e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        return BaseResponse(code=500, msg=msg)

    return BaseResponse(code=200, msg=f"已新增知识库 {knowledge_base_name}")


def delete_kb(
    knowledge_base_name: str = Body(..., examples=["samples"])
    ) -> BaseResponse:
    # Delete selected knowledge base
    if not validate_kb_name(knowledge_base_name):
        return BaseResponse(code=403, msg="Don't attack me")
    knowledge_base_name = urllib.parse.unquote(knowledge_base_name)

    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)

    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    try:
        status = kb.clear_vs()
        status = kb.drop_kb()
        if status:
            return BaseResponse(code=200, msg=f"成功删除知识库 {knowledge_base_name}")
    except Exception as e:
        msg = f"删除知识库时出现意外： {e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        return BaseResponse(code=500, msg=msg)

    return BaseResponse(code=500, msg=f"删除知识库失败 {knowledge_base_name}")


def ParseJson(schema: Json = Form({})) -> BaseResponse:
    print("schema", schema)
    try:
        # 对OpenAPI规范进行验证
        validate_spec(schema)
        print("The JSON file is a valid OpenAPI specification.")
        data = {}
        path = list(schema["paths"].keys())[0]
        method = list(schema["paths"][path].keys())[0]
        data["url"] = schema["servers"][0]["url"]
        data["path"] = path
        data["method"] = method
        data["operationId"] = schema["paths"][path][method]["operationId"]
        data["description"] = schema["paths"][path][method]["description"]
        data["parameters"] = schema["paths"][path][method]["parameters"]
        return BaseResponse(code=200, msg="success", data=data)
    except Exception as e:
        # 捕获所有验证过程中可能出现的异常
        print("The JSON file is not a valid OpenAPI specification.")
        print(str(e))
        return BaseResponse(code=500, msg="Invalid Json")


def CreateAPI(newAPI: Json = Form({})) -> BaseResponse:
    try: 
        print("newAPI", newAPI)
        newAPI_json = json.dumps(newAPI)
    
        # 获取当前脚本的绝对路径
        current_script_path = os.path.abspath(__file__)
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(current_script_path)
        # 构造api.jsonl文件的绝对路径
        file_path = os.path.join(current_dir, 'api.jsonl')
        
        # 打开或创建api.jsonl文件，并追加新的API数据
        with open(file_path, "a") as file:
            file.write(newAPI_json + "\n")
        return BaseResponse(code=200, msg="success")
    except Exception as e:
        return BaseResponse(code=500, msg="failed")

