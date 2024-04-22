from langchain.tools import Tool
from server.agent.tools import *
from server.agent.tools.knowledge_graph_search import knowledge_graph_search, KnowledgeGraphSearchInput

## 请注意，如果你是为了使用AgentLM，在这里，你应该使用英文版本。

tools = [
    # Tool.from_function(
    #     func=calculate,
    #     name="计算器工具",
    #     description="进行简单的数学运算, 只是简单的, 使用Wolfram数学工具进行更复杂的运算",
    #     args_schema=CalculatorInput,
    # ),
    # Tool.from_function(
    #     func=translate,
    #     name="翻译工具",
    #     description="如果你无法访问互联网，并且需要翻译各种语言，应该使用这个工具",
    #     args_schema=TranslateInput,
    # ),
    Tool.from_function(
        func=waterlevelcheck,
        name="水位查询工具",
        description="无需访问互联网，使用这个工具查询某个圩区的实时水位高度，水位信息常用来辅助进行防洪排涝调度方案决策",
        args_schema=WaterLevelSchema,
    ),
    # Tool.from_function(
    #     func=search_internet,
    #     name="互联网查询工具",
    #     description="如果你无法访问互联网，这个工具可以帮助你访问Bing互联网来解答问题",
    #     args_schema=SearchInternetInput,
    # ),
    Tool.from_function(
        func=search_express,
        name="快递查询",
        description="快递查询，用于自动识别快递公司及单号",
        args_schema=ExpressInput,
    ),
    Tool.from_function(
        func=search_weather,
        name="天气查询",
        description="天气查询，输入是一个location（类似于101010100）来进行当前天气的查询",
        args_schema=WeatherInput,
    )
]

tool_names = [tool.name for tool in tools]
