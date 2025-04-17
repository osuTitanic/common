
import ipaddress

def is_local_ip(ip: str) -> bool:
    """Check if the given IP address is a local IP address"""
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False

    return any((
        address.is_private,
        address.is_loopback,
        address.is_link_local,
        address.is_reserved,
        address.is_multicast,
        address.is_unspecified
    ))

def resolve_ip_address_flask(request):
    """Resolve the IP address of a flask request"""
    if ip := request.headers.get("CF-Connecting-IP"):
        return ip

    if forwards := request.headers.get("X-Forwarded-For"):
        return forwards.split(",")[0]

    if ip := request.headers.get("X-Real-IP"):
        return ip.strip()

    return request.environ['REMOTE_ADDR']

def resolve_ip_address_fastapi(request):
    """Resolve the IP address of a fastapi request"""
    if ip := request.headers.get("CF-Connecting-IP"):
        return ip

    if forwards := request.headers.get("X-Forwarded-For"):
        return forwards.split(",")[0]

    if ip := request.headers.get("X-Real-IP"):
        return ip

    return request.client.host.strip()

def resolve_ip_address_twisted(request):
    """Resolve the IP address of a twisted request"""
    if ip := request.requestHeaders.getRawHeaders("CF-Connecting-IP"):
        return ip[0]

    if forwards := request.requestHeaders.getRawHeaders("X-Forwarded-For"):
        return forwards[0]

    if ip := request.requestHeaders.getRawHeaders("X-Real-IP"):
        return ip[0]

    return request.getClientAddress().host.strip()

def resolve_ip_address_autobahn(request):
    """Resolve the IP address of an autobahn request"""
    if ip := request.headers.get("cf-connecting-ip"):
        return ip

    if forwards := request.headers.get("x-forwarded-for"):
        return forwards.split(",")[0].strip()

    if ip := request.headers.get("x-real-ip"):
        return ip.strip()

    peer = request.peer
    parts = peer.rsplit(":", 1)
    return parts[0] if len(parts) == 2 else peer
