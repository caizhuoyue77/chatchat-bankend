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
import requests

qweather_api_key = "7fa7d0d9ef374dc78c32fd8f5cb444b7"

def get_location_id(location):
    base_url = "https://geoapi.qweather.com/v2/city/lookup"
    params = {
        "key": qweather_api_key,
        "location": location
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        response_json = response.json()  # 首先获取整个JSON数据
        return response_json  # 返回JSON中的'data'部分，如果没有则返回空字典
    else:
        return {"error": "Failed to fetch tracking information"}


def get_current_weather(location):
    base_url = "https://devapi.qweather.com/v7/weather/now"
    params = {
        "key": qweather_api_key,
        "location":location
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        response_json = response.json()  # 首先获取整个JSON数据
        return response_json  
    else:
        return {"error": "Failed to fetch tracking information"}


def get_express_info(tracking_no):
    """
    根据提供的追踪号码查询快递信息。

    参数:
    - tracking_no: 快递的追踪号码。

    返回:
    - dict: API响应的字典对象。
    """
    # API的基本信息
    api_key = "你的API密钥"  # 替换为你的实际API密钥
    base_url = "http://api.tanshuapi.com/api/exp/v1/index"
    params = {
        "key": "5ee7419381ccb75f793ba094b9f80280",
        "com": "auto",
        "no": tracking_no,
        "phone": "9766"  # 根据需要修改或移除
    }

    # 发送GET请求
    response = requests.get(base_url, params=params)

    # 检查响应状态
    if response.status_code == 200:
        response_json = response.json()  # 首先获取整个JSON数据
        return response_json.get('data', {})  # 返回JSON中的'data'部分，如果没有则返回空字典
    else:
        return {"error": "Failed to fetch tracking information"}
