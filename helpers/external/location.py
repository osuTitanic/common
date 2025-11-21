
from __future__ import annotations

from ...constants import COUNTRIES
from ..ip import is_local_ip

from geoip2.errors import AddressNotFoundError
from geoip2.database import Reader

from dataclasses import dataclass
from functools import cache

import config
import app

@dataclass(slots=True)
class Geolocation:
    ip: str = '127.0.0.1'
    latitude: float = 0.0
    longitude: float = 0.0
    country_code: str = 'XX'
    country_name: str = 'Unknown'
    country_index: int = 0
    timezone: str = 'UTC'
    city: str = 'Unknown'

    @property
    def is_local(self) -> bool:
        return is_local_ip(self.ip)

    def set_country_code(self, code: str) -> None:
        if code not in COUNTRIES:
            self.country_code = 'XX'
            self.country_name = 'Unknown'
            self.country_index = 0
            return

        self.country_code = code
        self.country_name = COUNTRIES.get(code, 'Unknown')
        self.country_index = list(COUNTRIES.keys()).index(code)

@cache
def fetch_geolocation(ip: str) -> Geolocation:
    try:
        is_local = is_local_ip(ip)

        if is_local:
            # Resolve ip address of server
            if not (geo := fetch_web()):
                return Geolocation()

            return geo

        if (geo := fetch_db(ip)):
            return geo

        if (geo := fetch_web(ip)):
            return geo
    except Exception as e:
        app.session.logger.error(f'Failed to get geolocation: {e}')

    return Geolocation()

def fetch_db(ip: str) -> Geolocation | None:
    try:
        with Reader(f'./app/common/geolite.mmdb') as reader:
            response = reader.city(ip)

            return Geolocation(
                ip,
                response.location.latitude,
                response.location.longitude,
                response.country.iso_code,
                response.country.name,
                list(COUNTRIES.keys()).index(
                    response.country.iso_code
                ),
                response.location.time_zone,
                response.city.name
            )
    except AddressNotFoundError:
        return

def fetch_web(ip: str = "") -> Geolocation | None:
    try:
        response = app.session.requests.get(
            f'http://ip-api.com/line/{ip or ""}',
            allow_redirects=True,
            timeout=5
        )

        if not response.ok:
            return None

        status, *lines = response.text.split('\n')

        if status != 'success':
            app.session.logger.error(
                f'Failed to get geolocation: {status} ({lines[0]})'
            )
            return None

        index = list(COUNTRIES.keys()).index(lines[1])

        return Geolocation(
            ip=lines[12],
            latitude=float(lines[6]),
            longitude=float(lines[7]),
            country_code=lines[1],
            country_name=lines[0],
            country_index=index,
            timezone=lines[8],
            city=lines[4]
        )
    except Exception as e:
        app.session.logger.error(f'Failed to get geolocation from web: {e}')
        return None
