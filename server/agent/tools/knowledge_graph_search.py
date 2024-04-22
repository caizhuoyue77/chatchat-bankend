from __future__ import annotations

import asyncio

from pydantic import BaseModel, Field

from server.chat.knowledge_graph_chat import retrieve_knowledge_from_graph


async def knowledge_graph_search_a(query: str):
    retrieve_knowledge = await retrieve_knowledge_from_graph(query)
    return retrieve_knowledge


def knowledge_graph_search(query: str):
    return asyncio.run(knowledge_graph_search_a(query))


class KnowledgeGraphSearchInput(BaseModel):
    location: str = Field(description="想要在知识图谱查询的内容")


if __name__ == "__main__":
    result = knowledge_graph_search("位于红旗塘水系的闸站有哪些？")
    print(result)
