from langchain.tools import Tool
from server.agent.tools import *
from server.agent.tools.knowledge_graph_search import knowledge_graph_search, KnowledgeGraphSearchInput

## 请注意，如果你是为了使用AgentLM，在这里，你应该使用英文版本。

tools = [
    Tool.from_function(
        func=get_currency,
        name="获取不同货币信息",
        description="查询所有货币的货币码，例如CNY",
        args_schema=TimeInput,
    ),
    Tool.from_function(
        func=get_exchange_rates,
        name="获取货币汇率",
        description="查询人民币比其他货币的实时汇率",
        args_schema=TimeInput,
    ),
    Tool.from_function(
        func=get_languages,
        name="获取不同语言信息",
        description="查询所有语言的语言码，例如zh-cn",
        args_schema=TimeInput,
    ),
    Tool.from_function(
        func=get_location_to_lat_lon,
        name="转换位置到经纬度",
        description="根据提供的地点查询，返回对应的经纬度信息",
        args_schema=TimeInput,
    ),
    Tool.from_function(
        func=get_attraction_locations,
        name="搜索旅游景点的位置id和坐标",
        description="根据提供的地点查询旅游景点的位置id和坐标信息",
        args_schema=TimeInput,
    ),
    Tool.from_function(
        func=get_attraction_locations,
        name="搜索旅游景点详细信息",
        description="根据提供的旅游景点的位置id查询景点的详细信息",
        args_schema=TimeInput,
    ),
    Tool.from_function(
        func=get_attraction_locations,
        name="搜索旅游景点的位置id和坐标",
        description="根据提供的地点查询旅游景点的位置id和坐标信息",
        args_schema=TimeInput,
    ),
    Tool.from_function(
        func=get_flights,
        name="查询航班信息",
        description="查询航班的信息",
        args_schema=TimeInput,
    )
    Tool.from_function(
        func=fetch_hotels,
        name="查询酒店信息",
        description="查询某地点的酒店信息，返回详细的酒店信息",
        args_schema=TimeInput,
    ),
    Tool.from_function(
        func=imdb_top_100_movies,
        name="IMDB Top 100 Movies",
        description="从IMDB电影网站获取排名前100的电影",
        args_schema=TimeInput,
    ),
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
        name="24小时天气预报查询",
        description="天气预报查询，查询中国和全球城市天气的未来24小时预报数据，包括：温度、湿度、风向、风力等。",
        args_schema=WeatherInput,
    ),
     Tool.from_function(
        func=weather_forcast_24h,
        name="3天天气预报查询",
        description="天气预报查询，查询中国和全球城市天气的未来3天的天气预报数据，包括：温度、湿度、风向、风力等。",
        args_schema=WeatherInput,
    ),
     Tool.from_function(
        func=weather_forcast_24h,
        name="7天天气预报查询",
        description="天气预报查询，查询中国和全球城市天气的未来7天的天气预报数据，包括：温度、湿度、风向、风力等。",
        args_schema=WeatherInput,
    ),
     Tool.from_function(
        func=weather_rain_minute,
        name="分钟级降雨预报查询",
        description="分钟级别的降雨预报查询，精确到分钟级别，识别location（9位数字）",
        args_schema=WeatherInput,
    ),
    Tool.from_function(
        func=get_current_time,
        name="获取当前时间",
        description="获取当前时间，返回当前时间的字符串",
        args_schema=TimeInput,
    ),

]

tool_names = [tool.name for tool in tools]
