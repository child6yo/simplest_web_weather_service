from typing import NamedTuple
from urllib import request
import json

OPENMETEO_CURRENTWEATHER_URL = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&current=temperature_2m"


class Coordinates(NamedTuple):
    latitude: set
    longtitude: str


Celsius = int


class Weather(NamedTuple):
    temperature: Celsius


class OpenmeteoParcer:

    def __init__(self) -> None:
        """Current weather parcer from open-meteo.com

        (https://open-meteo.com/)"""
        self.currentweatherurl = OPENMETEO_CURRENTWEATHER_URL

    def get_weather(self, coordinates: Coordinates) -> Weather:
        """Return current weather by coordinates as Weather object."""
        url = self.__url_formatter(coordinates)
        raw_weather = self.__weather_parcer(url)
        weather = self.__weather_formatter(raw_weather)
        return weather

    def __weather_parcer(self, url: str) -> dict:
        with request.urlopen(url) as page:
            raw = json.load(page)
        return raw

    def __url_formatter(self, coordinates: Coordinates) -> str:
        latitude = coordinates.latitude
        longitude = coordinates.longtitude
        formatted_url = self.currentweatherurl.format(latitude, longitude)
        return formatted_url

    def __weather_formatter(self, raw_data: dict) -> Weather:
        temperature = int(raw_data["current"]["temperature_2m"])
        return Weather(
            temperature=temperature,
        )
