from typing import NamedTuple
from urllib import request
import json
from coordinates_service import Coordinates


Celsius = int


class Weather(NamedTuple):
    temperature: Celsius
    city: str


class OpenmeteoParcer:

    _currentweatherurl = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&current=temperature_2m"

    def get_weather(self, coordinates: Coordinates) -> Weather:
        url = self.__url_formatter(coordinates)
        raw_weather = self.__weather_parcer(url)
        weather = self.__weather_formatter(raw_weather, coordinates.city)
        return weather

    def __weather_parcer(self, url: str) -> dict:
        with request.urlopen(url) as page:
            raw = json.load(page)
        return raw

    def __url_formatter(self, coordinates: Coordinates) -> str:
        latitude = coordinates.latitude
        longitude = coordinates.longtitude
        formatted_url = self._currentweatherurl.format(latitude, longitude)
        return formatted_url

    def __weather_formatter(self, raw_data: dict, city_name: str) -> Weather:
        temperature = int(raw_data["current"]["temperature_2m"])
        city = city_name
        return Weather(
            temperature=temperature,
            city=city,
        )
