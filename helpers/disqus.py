
from typing import Dict, Any

import hashlib
import base64
import hmac
import json
import time

def hmacsha1(data: str, key: str) -> str:
    mac = hmac.new(
        key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha1
    )
    return mac.hexdigest()

def build_auth(user_payload: Dict[str, Any], secret_key: str) -> str:
    message_json = json.dumps(user_payload, separators=(',', ':'), ensure_ascii=False)
    message_b64 = base64.b64encode(message_json.encode()).decode()
    timestamp = str(int(time.time()))

    sig = hmacsha1(message_b64 + ' ' + timestamp, secret_key)
    return " ".join([message_b64, sig, timestamp])
