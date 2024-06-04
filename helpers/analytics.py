
# Modified amplitude api from:
# https://github.com/osuAkatsuki/score-service/blob/master/app/adapters/amplitude.py

from __future__ import annotations

from app.common.database.repositories import wrapper
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Mapping

import config
import time
import app

executor = ThreadPoolExecutor(max_workers=4)

def on_track_fail(e: Exception) -> None:
    app.session.logger.error(
        f"Failed to call amplitude api: {e}"
    )

def thread_wrapper(func):
    def wrapper(*args, **kwargs):
        executor.submit(
            func,
            *args,
            **kwargs
        )
    return wrapper

def ensure_api_key(func) -> None:
    def wrapper(*args, **kwargs) -> None:
        if not getattr(config, "AMPLITUDE_API_KEY", None):
            return
        return func(*args, **kwargs)
    return wrapper

@ensure_api_key
@thread_wrapper
@wrapper.exception_wrapper(on_track_fail)
def track(
    event_name: str,
    user_id: str | None = None,
    device_id: str | None = None,
    timestamp: int | None = None,
    event_properties: Mapping[str, Any] | None = None,
    user_properties: Mapping[str, Any] | None = None,
    groups: Mapping[str, Any] | None = None,
    app_version: str | None = None,
    platform: str | None = None,
    os_name: str | None = None,
    os_version: str | None = None,
    device_brand: str | None = None,
    device_manufacturer: str | None = None,
    device_model: str | None = None,
    carrier: str | None = None,
    country: str | None = None,
    region: str | None = None,
    city: str | None = None,
    dma: str | None = None,
    language: str | None = None,
    price: float | None = None,
    quantity: int | None = None,
    revenue: float | None = None,
    product_id: str | None = None,
    revenue_type: str | None = None,
    location_lat: float | None = None,
    location_lng: float | None = None,
    ip: str | None = None,
    idfa: str | None = None,
    idfv: str | None = None,
    adid: str | None = None,
    android_id: str | None = None,
    event_id: int | None = None,
    session_id: int | None = None,
    insert_id: str | None = None
) -> None:
    assert user_id or device_id, "Either user_id or device_id must be provided"

    # Create event payload
    amplitude_event = {
        "user_id": user_id,
        "device_id": device_id,
        "event_type": event_name,
        "time": timestamp or int(time.time() * 1000),
        "event_properties": event_properties or {},
        "user_properties": user_properties or {},
        "groups": groups,
        "app_version": app_version,
        "platform": platform,
        "os_name": os_name,
        "os_version": os_version,
        "device_brand": device_brand,
        "device_manufacturer": device_manufacturer,
        "device_model": device_model,
        "carrier": carrier,
        "country": country,
        "region": region,
        "city": city,
        "dma": dma,
        "language": language,
        "price": price,
        "quantity": quantity,
        "revenue": revenue,
        "product_id": product_id,
        "revenue_type": revenue_type,
        "location_lat": location_lat,
        "location_lng": location_lng,
        "ip": ip,
        "idfa": idfa,
        "idfv": idfv,
        "adid": adid,
        "android_id": android_id,
        "event_id": event_id,
        "session_id": session_id,
        "insert_id": insert_id,
    }

    # Filter out "None" values
    amplitude_event = {k: v for k, v in amplitude_event.items() if v is not None}

    response = app.session.requests.post(
        url="https://api.amplitude.com/2/httpapi",
        headers={"Content-Type": "application/json"},
        json={
            "api_key": config.AMPLITUDE_API_KEY,
            "events": [amplitude_event],
            "options": {
                "min_id_length": 1
            }
        },
        timeout=10
    )
    response.raise_for_status()
