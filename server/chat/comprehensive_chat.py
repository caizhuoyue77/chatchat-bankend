from fastapi import Body, Request
from fastapi.responses import StreamingResponse
from configs import (LLM_MODELS, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, TEMPERATURE, logger)
from server.chat.agent_chat import agent_chat
from server.chat.knowledge_graph_chat import retrieve_knowledge_from_graph
from server.utils import wrap_done, get_ChatOpenAI
from server.utils import BaseResponse, get_prompt_template
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable, List, Optional
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from server.chat.utils import History
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.knowledge_base.utils import get_doc_path
import json
from pathlib import Path
from urllib.parse import urlencode
from server.knowledge_base.kb_doc_api import search_docs
from server.chat.search_engine_chat import lookup_search_engine


async def agent_iter(query: str):
    response = await agent_chat(query=query,
                                model_name="azure-api",
                                temperature=0.3,  # Agent 搜索互联网的时候，温度设置为0.01
                                history=[],
                                # top_k = VECTOR_SEARCH_TOP_K,
                                max_tokens=2000,
                                prompt_name="中文版本",
                                stream=False)

    contents = ""

    async for data in response.body_iterator:  # 这里的data是一个json字符串
        data = json.loads(data)
        contents = data["final_answer"]
        docs = data["answer"]

    return contents

async def call_agent(query):
    try:
        logger.info("开始调用Agent")
        agent_response = await agent_iter(query)
    except Exception as e:
        logger.error(f"Agent调用失败: {e}")
        agent_response = ""
    return agent_response



async def comprehensive_chat(query: str = Body(..., description="用户输入", examples=["你好"]),
                             knowledge_base_name: str = Body(..., description="知识库名称", examples=["samples"]),
                             top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                             score_threshold: float = Body(SCORE_THRESHOLD,
                                                           description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右",
                                                           ge=0, le=2),
                             history: List[History] = Body([],
                                                           description="历史对话",
                                                           examples=[[
                                                               {"role": "user",
                                                                "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                               {"role": "assistant",
                                                                "content": "虎头虎脑"}]]
                                                           ),
                             stream: bool = Body(False, description="流式输出"),
                             model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
                             temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                             max_tokens: Optional[int] = Body(None,
                                                              description="限制LLM生成Token数量，默认None代表模型最大值"),
                             prompt_name: str = Body("default",
                                                     description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                             request: Request = None,
                             ):
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}")

    history = [History.from_data(h) for h in history]

    async def comprehensive_chat_iterator(query: str,
                                          top_k: int,
                                          history: Optional[List[History]],
                                          model_name: str = LLM_MODELS[0],
                                          prompt_name: str = prompt_name,
                                          ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            callbacks=[callback],
        )


        # 知识图谱查询
        # retrieve_knowledge = await retrieve_knowledge_from_graph(query)
        retrieve_knowledge = {"knowledge": "[]"}

        # 向量知识库查询
        docs = search_docs(query, knowledge_base_name, top_k, score_threshold)
        # 搜索引擎查询
        # search_reseult = await lookup_search_engine(query, "bing", 3)

        context = ""

        if retrieve_knowledge["knowledge"] != "[]":
            context += "知识图谱中检索到的该问题答案是：" + retrieve_knowledge["knowledge"] + "\n"

        if len(docs) != 0:
            context += "文档知识库中检索到的相关知识是：" + "\n".join([doc.page_content for doc in docs]) + "\n"

        # 如果Agent回复不为空，且回复中不包含失败字样
        # if agent_response != "" and "失败" not in agent_response:
        #     context += "相关领域知识agent的检索的结果是：" + agent_response + "\n"

        # if len(search_reseult) != 0:
        #     context += "互联网上检索到的相关知识是：" + "\n".join([doc.page_content for doc in search_reseult])

        print("最终检索到的知识为{}".format(context))


        # 判断是否检索到外部知识
        if context == "":
            prompt_template = get_prompt_template("knowledge_base_chat", "Empty")
        else:
            prompt_template = get_prompt_template("knowledge_base_chat", prompt_name)

        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])

        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        task = asyncio.create_task(wrap_done(
            chain.acall({"context": context, "question": query}),
            callback.done),
        )

        source_documents = []

        # 如果知识库里查到了信息
        doc_path = get_doc_path(knowledge_base_name)
        index = 1
        for inum, doc in enumerate(docs):
            filename = Path(doc.metadata["source"]).resolve().relative_to(doc_path)
            parameters = urlencode({"knowledge_base_name": knowledge_base_name, "file_name": filename})
            base_url = request.base_url
            url = f"{base_url}knowledge_base/download_doc?" + parameters
            text = f"""出处 [{index}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
            source_documents.append(text)
            index += 1

        # 如果知识图谱里查到了信息
        if retrieve_knowledge["knowledge"] != "[]":
            source_documents.append(
                f"""出处 [{docs.__len__() + 1}] [知识图谱](http://dgraph.askgraph.site/)\n\n 知识图谱中检索到的相关知识是{retrieve_knowledge["knowledge"]}""")

        # # 如果Agent中查到了信息
        # if agent_response != "" and "失败" not in agent_response:
        #     source_documents.append(
        #         f"""出处 [{docs.__len__() + 2}] [Agent]\n\n 相关领域知识agent的检索的结果是{agent_response}""")

        # 如果搜索引擎中查到了信息
        # temp_index = source_documents.__len__()
        # for inum, doc in enumerate(search_reseult):
        #     source_documents.append(
        #         f"""出处 [{temp_index + inum + 1}]
        #         [{doc.metadata["source"]}]({doc.metadata["source"]}) \n\n{doc.page_content}\n\n""")

        if len(source_documents) == 0:  # 没有找到相关文档
            source_documents.append(f"""<span style='color:red'>未找到相关知识,该回答为大模型自身能力解答！</span>""")

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps({"answer": token}, ensure_ascii=False)
            yield json.dumps({"docs": source_documents}, ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": answer,
                              "docs": source_documents},
                             ensure_ascii=False)
        await task

    return StreamingResponse(comprehensive_chat_iterator(query=query,
                                                         top_k=top_k,
                                                         history=history,
                                                         model_name=model_name,
                                                         prompt_name=prompt_name),
                             media_type="text/event-stream")
