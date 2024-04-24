from langchain.tools import Tool
from server.agent.tools import *
from server.agent.tools.knowledge_graph_search import knowledge_graph_search, KnowledgeGraphSearchInput

## 请注意，如果你是为了使用AgentLM，在这里，你应该使用英文版本。

tools = [
    Tool.from_function(
        func=waterlevelcheck,
        name="水位查询工具",
        description="无需访问互联网，使用这个工具查询某个圩区的实时水位高度，水位信息常用来辅助进行防洪排涝调度方案决策",
        args_schema=WaterLevelSchema,
    ),
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
    ),
    Tool.from_function(
        func=search_location,
        name="地点查询",
        description="地点查询，用于自动识别location，只需要返回一个8位数字的location，例如101010100",
        args_schema=LocationInput,
    ),
    Tool.from_function(
        func=sunrise_sunset,
        name="日出日落查询",
        description="日出日落查询，用于自动识别location，只需要返回一个8位数字的location，例如101010100",
        args_schema=SunriseSunsetInput,
    ),
]

tool_names = [tool.name for tool in tools]
