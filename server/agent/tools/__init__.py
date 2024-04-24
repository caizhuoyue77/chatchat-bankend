## 导入所有的工具类
from .search_knowledge_simple import knowledge_search_simple
from .search_all_knowledge_once import knowledge_search_once, KnowledgeSearchInput
from .search_all_knowledge_more import knowledge_search_more, KnowledgeSearchInput
from .calculate import calculate, CalculatorInput
from .translator import translate, TranslateInput
from .weather import weathercheck, WhetherSchema
from .water_level import waterlevelcheck, WaterLevelSchema
from .shell import shell, ShellInput
from .search_internet import search_internet, SearchInternetInput
from .wolfram import wolfram, WolframInput
from .youtube import youtube_search, YoutubeInput
from server.agent.tools.search_express import search_express, ExpressInput
from server.agent.tools.search_weather import search_weather, WeatherInput
from server.agent.tools.search_location import search_location, LocationInput
from server.agent.tools.sunrise_sunset import sunrise_sunset, SunriseSunsetInput