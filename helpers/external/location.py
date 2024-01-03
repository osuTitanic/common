
from __future__ import annotations

from ...constants import COUNTRIES

from geoip2.errors import AddressNotFoundError
from geoip2.database import Reader

from dataclasses import dataclass
from functools import cache

import ipaddress
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

def download_database():
    app.session.logger.info('Downloading geolite database...')

    response = app.session.requests.get(config.IP_DATABASE_URL)

    if not response.ok:
        app.session.logger.error(f'Download failed. ({response.status_code})')
        app.session.logger.warning('Skipping...')
        return

    with open(f'{config.DATA_PATH}/geolite.mmdb', 'wb') as f:
        f.write(response.content)

def is_local_ip(ip: str) -> bool:
    address = ipaddress.ip_address(ip)

    if address.version == 6:
        private = [
            ipaddress.IPv6Network('fc00::/7'),
            ipaddress.IPv6Network('::1/128')
        ]

        for net in private:
            if address in net:
                return True

        return False

    private = [
        ipaddress.IPv4Network('127.0.0.0/8'),
        ipaddress.IPv4Network('192.168.0.0/16'),
        ipaddress.IPv4Network('172.16.0.0/12'),
        ipaddress.IPv4Network('10.0.0.0/8')
    ]

    for net in private:
        if address in net:
            return True

    return False

@cache
def fetch_geolocation(ip: str) -> Geolocation:
    try:
        is_local = is_local_ip(ip)

        if is_local:
            if not (geo := fetch_web(ip, is_local)):
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

def fetch_web(ip: str, is_local: bool = False) -> Geolocation | None:
    try:
        response = app.session.requests.get(f'http://ip-api.com/line/{ip if not is_local else ""}')

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
