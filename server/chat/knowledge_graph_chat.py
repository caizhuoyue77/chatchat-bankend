from fastapi import Body
from fastapi.responses import StreamingResponse
from langchain.schema import Document

from configs import (LLM_MODELS, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, TEMPERATURE, KB_ROOT_PATH)
from server.knowledge_base.kb_doc_api import upload_docs, search_docs
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.knowledge_base.utils import validate_kb_name
from server.utils import wrap_done, get_ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from typing import List
from server.chat.utils import History
from server.utils import get_prompt_template

import json
import os
import requests
import httpx
import uuid
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI


llm = ChatOpenAI(openai_api_key="", temperature=0,
                 openai_api_base="https://api.openai-sb.com/v1", request_timeout=5)
base_url = "http://47.94.3.221:9176/"

prompt_entity_linking = PromptTemplate.from_template("""
你是一个非常优秀的本体模型链接专家。
你的任务是将用户问题中的涉及到的实体和知识图谱相应本体模型中的概念链接起来。
要求:
1. 你只能从给定的概念列表中选择概念来链接问题中的实体。不能使用未提供的概念。
2. 如果图谱中有多个概念与问题中的实体可能链接，你可以选择所有可能涉及的概念。
3. 请使用以下Json格式输出概念:
["概念1", "概念2", ... ,"概念N"]
例子1:
问题: 
请问姓陈的司机有哪些？
概念列表:
['司机', '派车时间', '担架员', '体征', '时间']
链接结果: 
["司机"]

例子2:
问题:
请问警戒水位大于1.3m的闸站有哪些？
概念列表:
['泵站', '闸站', '水利工程', '运管单位', '测站']
链接结果: 
["闸站"]

例子3:
问题:
足球运动员梅西的足球俱乐部是什么？
概念列表:
['国家', '俱乐部', '薪资', '运动员']
链接结果: 
["运动员", "俱乐部"]

问题:
{question}
实体列表:
{concepts}
链接结果:
""")

# prompt_gremlin_generate = PromptTemplate(
#     input_variables=["centerConcept", "properties", "edgeLabels", "edges", "question"], template="""
# 请帮我写Gremlin，在写的时候务必遵守以下规则，
# 标签分为三种：一种是概念标签，包括：{centerConcept}，一种是属性标签，包括：{properties}，一种是关系标签，包括：{edgeLabels}，
# 所有的编写gremlin时的标签都只能在这个范围内选择,并且不能篡改原有标签的内容；
# 每个节点都会有name属性；概念标签也可以被称为节点的类型，只能用于检索点的类型，形如g.V().has(T.label,\"概念标签\")；
# 关系标签只能用于检索边的类型，形如g.V().out(\"关系标签\"))；属性标签只能用于检索时的属性名，形如g.V().has(\"属性标签\",11)；
# 请注意标签检索用has(T.label,\"标签\")，不要用hasLabel；请注意只存在这些关系：{edges}，其他的类型对之间一概不存在关系；
# 如果是字符串包含请用containing，而不是contains；
# id的检索用g.V(id)；
# 我在冒号后面会给出需要检索的需求，你只需要回答我Gremlin语句，多余的话一个字也不要说：{question}
# """)

prompt_gremlin_generate_head = """
请根据知识图谱本体模型中的概念、属性、关系，回答相应的Gremlin检索语句来解答用户问题。
概念标签也可以被称为节点的类型，只能用于检索点的类型，形如g.V().has(T.label,\"概念标签\")；
每个节点都会有name属性；
关系标签只能用于检索边的类型，形如g.V().out(\"关系标签\"))；属性标签只能用于检索时的属性名，形如g.V().has(\"属性标签\",11)；

"""

prompt_gremlin_generate_tail = """
概念标签：
{centerConcept}
属性标签：
{properties}
关系标签：
{edgeLabels}
关系三元组：
{edges}
问题：
{question}
Gremlin:
"""
prompt_gremlin_generate = PromptTemplate(
    input_variables=["centerConcept", "properties", "edgeLabels", "edges", "question"], template="""
请根据知识图谱本体模型中的概念、属性、关系，回答相应的Gremlin检索语句来解答用户问题。
概念标签也可以被称为节点的类型，只能用于检索点的类型，形如g.V().has(T.label,\"概念标签\")；
每个节点都会有name属性；
关系标签只能用于检索边的类型，形如g.V().out(\"关系标签\"))；属性标签只能用于检索时的属性名，形如g.V().has(\"属性标签\",11)；

示例1：
概念标签：
['泵站',]
属性标签：
['id*', '名称', '管理层级', '所属行政区', '行政区划编码', '所在水系', '工程规模', '工程等别', '工程任务', '泵站类型', '水泵数量', '装机流量', '装机功率', '设计扬程', '参考水位站名称', '水位站警戒水位', '水位站危机水位', '内河常水位', '年度灌溉引水水量', '年度防洪排涝水量', 'name']
关系标签：
['位于', '管理']
关系三元组：
['运管单位-管理->泵站', '泵站-位于->水系']
问题：
一共有多少泵站？
Gremlin:
g.V().has(T.label, "泵站").count()

示例2：
概念标签：
['运管单位'] 
属性标签：
['所属行政区', '行政区划编码', '圩区面积', '水田面积', '水文代表站名称', '水文代表站警戒水位', '水文代表站保证水位', '保护对象类别', 
'保护村庄集镇数量', '重要保护对象数量', '保护城市人口', '防洪标准', '排涝标准', '建后管理单位', '起排水位', '建设完成时间', '设计流量', '投资', '正常退出水位', '开工时间', 
'工程使用年限', '工程建设单位', '工程设计单位', '工程施工单位', '工程监理单位', '名称*', 'name'] 
关系标签：
['位于', '管理', '任职', '制定'] 
关系三元组： ['运管单位-管理->闸站', '运管单位-管理->泵站', '运管单位-管理->堤防', '运管单位-管理->枢纽', '运管单位-管理->测站', '管理人员-任职->运管单位', 
'运管单位-制定->调度方案', '运管单位-位于->行政区'] 
问题： 
名字包含王家圩区的运管单位有哪些？
Gremlin：
g.V().has(T.label, '运管单位').has('name', containing('王家圩区'))

示例3：
概念标签：
["闸站", "运管单位"] 
属性标签：
['id*', '名称', '管理层级', '所属行政区', '行政区划编码', '所在水系', '所属工程', '工程规模', '闸孔数量', '闸孔净宽', 
'闸孔总净宽', '水闸设计过闸流量', '水闸设计洪水标准', '参考水位站名称', '水位站警戒水位', '水位站危机水位', '内河常水位', '内外河历史最高潮位', '内外河历史最低潮位', '历史最大流量', 
'防洪保护-重要对象', '设计灌溉面积', '所属行政区', '行政区划编码', '圩区面积', '水田面积', '水文代表站名称', '水文代表站警戒水位', '水文代表站保证水位', '保护对象类别', '保护村庄集镇数量', 
'重要保护对象数量', '保护城市人口', '防洪标准', '排涝标准', '建后管理单位', '起排水位', '建设完成时间', '设计流量', '投资', '正常退出水位', '开工时间', '工程使用年限', '工程建设单位', 
'工程设计单位', '工程施工单位', '工程监理单位', '名称*', 'name']
关系标签：
['位于', '管理', '任职', '制定']
关系三元组：
['运管单位-管理->闸站', '运管单位-管理->泵站', 
'运管单位-管理->堤防', '运管单位-管理->枢纽', '运管单位-管理->测站', '管理人员-任职->运管单位', '运管单位-制定->调度方案', '闸站-位于->水系', '运管单位-位于->行政区']
问题： 
冯家港圩区管理的闸站有哪些？（圩区是运管单位的一种）
Gremlin: 
g.V().has(T.label, '运管单位').has('name', containing('冯家港圩区')).out('管理').has(T.label, '闸站').values('名称')

示例4：
概念标签：
['泵站',]
属性标签：
['id*', '名称', '管理层级', '所属行政区', '行政区划编码', '所在水系', '工程规模', '工程等别', '工程任务', '泵站类型', '水泵数量', '装机流量', '装机功率', '设计扬程', 
'参考水位站名称', '水位站警戒水位', '水位站危机水位', '内河常水位', '年度灌溉引水水量', '年度防洪排涝水量', 'name']
关系标签：
['位于', '管理']
关系三元组：
['运管单位-管理->泵站', '泵站-位于->水系']
问题：
工程规模大于3的泵站有哪些？
Gremlin:
g.V().has(T.label, "泵站").has('工程规模', lt('3')).values('名称')

示例5：
概念标签：
['闸站', '水系']
属性标签：
['id*', '名称', '管理层级', '所属行政区', '行政区划编码', '所在水系', '所属工程', '工程规模', '闸孔数量', '闸孔净宽', '闸孔总净宽', '水闸设计过闸流量', '水闸设计洪水标准', 
'参考水位站名称', '水位站警戒水位', '水位站危机水位', '内河常水位', '内外河历史最高潮位', '内外河历史最低潮位', '历史最大流量', '防洪保护-重要对象', '设计灌溉面积', 
'河道起始点', '河道终止点', '名称*', 'name']
关系标签：
['位于', '管理']
关系三元组：
['运管单位-管理->闸站', '闸站-位于->水系', '泵站-位于->水系']
问题：
位于红旗塘水系的闸站有哪些？
Gremlin:
g.V().has(T.label, '水系').has('name', containing('红旗塘')).in('位于').has(T.label, '闸站').values('名称')

概念标签：
{centerConcept}
属性标签：
{properties}
关系标签：
{edgeLabels}
关系三元组：
{edges}
问题：
{question}
Gremlin:
""")

prompt_knowledge2answer = PromptTemplate(input_variables=["question", "knowledge"], template="""
请你根据答案来回答自然语言问题，在回答的时候只能根据给定的答案回答问题，不能凭空捏造答案。

示例1：
问题：
请问姓陈的司机有多少？
答案：
[253]
回答：
姓陈的司机有253个。

问题：
{question}
答案：
{knowledge}
回答：
""")


# knowledge2answer_chain = LLMChain(llm=llm, prompt=prompt_knowledge2answer, output_key="answer", verbose=True)

def query_preprocess(query):
    if "圩区" in query:
        query = query + "(圩区是运管单位的一种)"
    return query


async def get_ont_model():
    url_get_ont = base_url + "/v1/KGQA/getOntologyForLangchain"
    async with httpx.AsyncClient() as client:
        response = await client.get(url_get_ont)
        return response.json() if response.status_code == 200 else None


async def entity_linking(query):
    concepts = query["concepts"]
    question = query["query"]
    print(question)
    response = "[]"
    entity_linking_chain = LLMChain(llm=llm, prompt=prompt_entity_linking, output_key="entity_linking_result",
                                    verbose=True)
    # 如果一次请求失败，可以再次请求
    for i in range(3):
        try:
            # 如果请求超过了5秒，就抛出异常
            response = await entity_linking_chain.arun({"concepts": concepts, "question": question})
            # entity_linking_result = json.loads(response)
            print(response)
            return response
        except:
            continue
    return "[]"


async def get_core_concepts(query, linking_result):
    url_get_core_concepts = base_url + "/v1/KGQA/getCoreConceptsForLangchain"
    async with httpx.AsyncClient() as client:
        response = await client.get(url_get_core_concepts,
                                    params={"linking_result": linking_result, "query": query})
        return response.json() if response.status_code == 200 else None


async def query2gremlin(query, prompt):
    concepts = query["concepts"]
    edgeLabels = query["edgeLabels"]
    edges = query["edges"]
    properties = query["properties"]
    question = query["query"]
    gremlin_generate_chain = LLMChain(llm=llm, prompt=PromptTemplate(
        input_variables=["centerConcept", "properties", "edgeLabels", "edges", "question"], template=prompt),
                                      output_key="gremlin_result",
                                      verbose=True)
    for i in range(3):
        try:
            print("第" + str(i) + "次尝试")
            gremlin_generate_result = await gremlin_generate_chain.arun(
                {"centerConcept": concepts, "properties": properties, "edgeLabels": edgeLabels, "edges": edges,
                 "question": question})
            # gremlin_generate_result_json = json.loads(gremlin_generate_result)
            # print(gremlin_generate_result_json["gremlin"])
            print(gremlin_generate_result)
            return gremlin_generate_result
        except:
            continue
    print("gremlin生成失败")
    return ""


async def get_gremlin_execution_result(gremlin_generate_result):
    url_get_gremlin_execution_result = base_url + "/v1/KGQA/getGremlinResultForLangchain"
    async with httpx.AsyncClient() as client:
        response = await client.get(url_get_gremlin_execution_result, params={"gremlin": gremlin_generate_result})
        return response.json() if response.status_code == 200 else {"knowledge": "[]"}


def knowledge2answer(query):
    knowledge = query["knowledge"]
    question = query["query"]

    # prompt_konwledge2answer.format(question=question, knowledge=knowledge)
    return prompt_knowledge2answer.format(question=question, knowledge=knowledge)

    # response = "你好，我是知识问答系统，我还在学习中，暂时无法回答你的问题。"
    # for i in range(3):
    #     try:
    #         response = konwledge2answer_chain.run({"knowledge": knowledge, "question": question})
    #         print(response)
    #         return response
    #     except:
    #         continue
    # return response


# url_get_ont = "http://localhost:9176/v1/KGQA/getOntologyForLangchain"
# url_get_coreConcepts = "http://localhost:9176/v1/KGQA/getCoreConceptsForLangchain"
# url_get_gremlin = "http://localhost:9176/v1/KGQA/getGremlinResultForLangchain"

def store_sample_to_json(sample_data):
    """
    Store the sample data with a UUID and timestamp to a JSON file.

    Parameters:
    - sample_data (dict): The sample data to be stored.

    Returns:
    - str: The filename where the data was stored.
    """

    # Generate a UUID for the sample.
    # sample_id = str(uuid.uuid4())

    # Add a timestamp to the sample data.
    sample_data['timestamp'] = datetime.now().isoformat()

    # Set the filename to the UUID.
    filename = f"{sample_data['id']}.json"

    # Write the data to the file.
    complete_file_name = os.path.join(KB_ROOT_PATH, "KGQA", 'samples', filename)
    with open(complete_file_name, 'w', encoding='utf-8') as file:
        json.dump(sample_data, file, indent=4, ensure_ascii=False)

    return complete_file_name


# 存储历史样例到向量数据库
async def store_sample_to_vector_db(query, id):
    knowledge_base_name = "KGQA"
    if not validate_kb_name(knowledge_base_name):
        return

    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return
    docs = [Document(page_content=query, metadata={'source': id})]
    kb.do_add_doc(docs)
    kb.save_vector_store()


def read_json_from_uuid(uuid):
    file_path = os.path.join(KB_ROOT_PATH, "KGQA", 'samples', f"{uuid}.json")
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def construct_prompt_from_sample(sample):
    # 根据你的需求来构建prompt，这只是一个基础的示例
    return (f"概念标签\n: {sample['core_concepts']['concepts']}\n"
            f"属性标签:\n {sample['core_concepts']['properties']}\n"
            f"关系标签:\n {sample['core_concepts']['edgeLabels']}\n"
            f"关系三元组:\n {sample['core_concepts']['edges']}\n"
            f"问题:\n {sample['query']}\n"
            f"Gremlin:\n {sample['gremlin']}\n")


def generate_prompts_from_uuids(uuids):
    prompts = []
    for uuid in uuids:
        sample = read_json_from_uuid(uuid)
        prompt = construct_prompt_from_sample(sample)
        prompts.append(prompt)
    # 将所有的prompt拼接起来，中间用案例k衔接，k表示第几个案例
    prompt_template = "\n".join([f"示例{k + 1}：\n{prompt}" for k, prompt in enumerate(prompts)])
    # 之后在首尾加上相应的描述
    prompt_template = prompt_gremlin_generate_head + prompt_template + prompt_gremlin_generate_tail
    return prompt_template


async def retrieve_knowledge_from_graph(query: str):
    # 需要先对query进行一个预处理
    query = query_preprocess(query)

    docs = search_docs(query, "KGQA", 2, 1)
    context = "\n".join([doc.page_content for doc in docs])
    source = "\n".join([doc.metadata['source'] for doc in docs])

    prompt_gremlin_generate = generate_prompts_from_uuids([doc.metadata['source'] for doc in docs])

    ont_model = await get_ont_model()
    ont_model["query"] = query

    entity_linking_result = await entity_linking(ont_model)
    print(entity_linking_result)

    core_concepts = await get_core_concepts(query, entity_linking_result)
    core_concepts["query"] = query

    gremlin_generate_result = await query2gremlin(core_concepts, prompt_gremlin_generate)
    print(gremlin_generate_result)

    gremlin_execution_result = await get_gremlin_execution_result(gremlin_generate_result)
    gremlin_execution_result["query"] = query

    # 处理检索到的知识
    if gremlin_execution_result["knowledge"] != "[]":
        # 可以根据需求处理和格式化知识
        sample_id = str(uuid.uuid4())
        store_sample_to_json({
            'id': sample_id,
            "query": query,
            "gremlin": gremlin_generate_result,
            "core_concepts": core_concepts,
            "entity_linking": entity_linking_result,
            "gremlin_execution": gremlin_execution_result
        })
        await store_sample_to_vector_db(query, sample_id)
    return gremlin_execution_result


async def knowledge_graph_chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
                               history: List[History] = Body([],
                                                             description="历史对话",
                                                             examples=[[
                                                                 {"role": "user",
                                                                  "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                                 {"role": "assistant", "content": "虎头虎脑"}]]
                                                             ),
                               stream: bool = Body(False, description="流式输出"),
                               model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
                               temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                               # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
                               prompt_name: str = Body("llm_chat",
                                                       description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                               ):
    history = [History.from_data(h) for h in history]

    async def chat_iterator(query: str,
                            history: List[History] = [],
                            model_name: str = LLM_MODELS[0],
                            prompt_name: str = prompt_name,
                            ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()

        retrieve_knowledge = await retrieve_knowledge_from_graph(query)

        if retrieve_knowledge["knowledge"] == "[]":
            yield json.dumps({"answer": "知识图谱中未找到您问题的答案，请您换一种问法试试。",
                              "source_knowledge": "未检索到相关知识"},
                             ensure_ascii=False)
            return

        answer_prompt = knowledge2answer(retrieve_knowledge)
        print(answer_prompt)

        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            callbacks=[callback],
        )

        prompt_template = get_prompt_template("llm_chat", prompt_name)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])
        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"input": answer_prompt}),
            callback.done),
        )

        source_knowledge = f"""{retrieve_knowledge["knowledge"]}"""

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps({"answer": token}, ensure_ascii=False)
            yield json.dumps({"source_knowledge": source_knowledge}, ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": answer,
                              "source_knowledge": source_knowledge},
                             ensure_ascii=False)
        await task

    return StreamingResponse(chat_iterator(query=query,
                                           history=history,
                                           model_name=model_name,
                                           prompt_name=prompt_name),
                             media_type="text/event-stream")
