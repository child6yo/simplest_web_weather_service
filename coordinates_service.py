from typing import NamedTuple
from urllib import request
import json


class Coordinates(NamedTuple):
    latitude: str
    longtitude: str
    city: str


class GetCoordinates:

    def get_coordinates(self, ip_address: str) -> Coordinates:
        ip_info = self._ip_info_parcer(ip_address)
        lat = ip_info["latitude"]
        lon = ip_info["longitude"]
        city = ip_info["city"]
        return Coordinates(latitude=lat, longtitude=lon, city=city)

    def _ip_info_parcer(self, ip_address: str) -> dict:
        url = "https://ipapi.co/{}/json/"
        req = request.Request(url=url.format(ip_address), method="GET")
        with request.urlopen(req) as page:
            data = json.load(page)
        return data
