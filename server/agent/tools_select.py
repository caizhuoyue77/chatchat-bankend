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
        name="当前天气查询",
        description="当前天气查询，输入是一个location（类似于101010100）来进行当前天气的查询",
        args_schema=WeatherInput,
    ),
    Tool.from_function(
        func=search_location,
        name="地点id查询",
        description="地点查询，用于自动识别location，只需要返回一个8位数字的location，例如101010100",
        args_schema=LocationInput,
    ),
    Tool.from_function(
        func=sunrise_sunset,
        name="日出日落查询",
        description="日出日落查询，用于自动识别location和date。需要返回一个9位数字的location（如101010100）。和一个8位数的日期（如20240428），中间用逗号分隔开。",
        args_schema=WeatherInput,
    ),
     Tool.from_function(
        func=weather_index_1d,
        name="天气指数查询",
        description="天气指数查询，查询中国和全球城市天气的一天的生活指数预报数据，生活指数包括：舒适度指数、洗车指数、穿衣指数、感冒指数、运动指数、旅游指数等。",
        args_schema=WeatherInput,
    ),
     Tool.from_function(
        func=weather_forcast_24h,
        name="天气预报查询",
        description="天气预报查询，查询中国和全球城市天气的未来24小时预报数据，包括：温度、湿度、风向、风力等。",
        args_schema=WeatherInput,
    ),
     Tool.from_function(
        func=weather_rain_minute,
        name="分钟级降雨预报查询",
        description="分钟级别的降雨预报查询，精确到分钟级别，识别location（9位数字）",
        args_schema=WeatherInput,
    ),
]

tool_names = [tool.name for tool in tools]
