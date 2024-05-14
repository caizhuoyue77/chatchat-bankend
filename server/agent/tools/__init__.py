## 导入所有的工具类
from .search_knowledge_simple import knowledge_search_simple
from .search_all_knowledge_once import knowledge_search_once, KnowledgeSearchInput
from .search_all_knowledge_more import knowledge_search_more, KnowledgeSearchInput
from .weather import weathercheck, WhetherSchema
from .water_level import waterlevelcheck, WaterLevelSchema
from server.agent.tools.search_express import search_express, ExpressInput
from server.agent.tools.search_weather import search_weather, WeatherInput
from server.agent.tools.search_location import search_location, LocationInput
from server.agent.tools.sunrise_sunset import sunrise_sunset, WeatherInput
from server.agent.tools.weather_forcast_24h import weather_forcast_24h
from server.agent.tools.weather_rain_minute import weather_rain_minute
from server.agent.tools.weather_forcast_3d import weather_forcast_3d
from server.agent.tools.weather_forcast_7d import weather_forcast_7d
from server.agent.tools.weather_index_1d import weather_index_1d
from server.agent.tools.get_current_time import get_current_time, TimeInput
# from server.agent.tools.bookings_search_hotel_destination import search_hotel_destination, HotelDestinationInput
# from server.agent.tools.bookings_search_attraction_locations import get_attraction_locations, AttractionLocationSearchInput
# from server.agent.tools.bookings_search_attractions import get_attractions, AttractionSearchInput
from server.agent.tools.bookings_get_currency import get_currency
from server.agent.tools.bookings_get_exchange_rates import get_exchange_rates
from server.agent.tools.bookings_get_languages import get_languages
from server.agent.tools.bookings_location_to_lat_lon import get_location_to_lat_lon
from server.agent.tools.bookings_search_attractions import search_attractions
from server.agent.tools.bookings_search_flights import search_flights
from server.agent.tools.bookings_search_hotels import search_hotels


