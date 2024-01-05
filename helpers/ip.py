
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
