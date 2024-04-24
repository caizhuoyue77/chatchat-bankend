from langchain.tools import Tool
from server.agent.tools import *

## 请注意，如果你是为了使用AgentLM，在这里，你应该使用英文版本。

tools = [
    Tool.from_function(
        func=search_current_weather,
        name="天气查询",
        description="天气查询，输入是一个location（类似于101010100）来进行当前天气的查询",
        args_schema=WeatherInput,
    ),
    Tool.from_function(
        func=search_location_id,
        name="城市查询",
        description="城市location id查询，输入是一个城市名称，比如changsha，输出对应城市的location id",
        args_schema=LocationInput,
    )
]

tool_names = [tool.name for tool in tools]
