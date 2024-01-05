
import ipaddress

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

def resolve_ip_address_flask(request):
    """Resolve the IP address of a flask request"""
    ip = request.headers.get("CF-Connecting-IP")
    forwards = None

    if ip is None:
        forwards = request.headers.get("X-Forwarded-For")

    if forwards:
        ip = forwards.split(",")[0]
    else:
        ip = request.headers.get("X-Real-IP")

    if ip is None:
        ip = request.environ['REMOTE_ADDR']

    return ip.strip()

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
