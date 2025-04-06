
import re

CHROME = re.compile(r'Chrome/([7-9][0-9]|[1-9][0-9]{2,})')
FIREFOX = re.compile(r'Firefox/([6-9][0-9]|[1-9][0-9]{2,})')
SAFARI = re.compile(r'Version/(1[2-9]|[2-9][0-9])\.\d+')
EDGE = re.compile(r'Edg/([7-9][9-9]|[1-9][0-9]{2,})')
OPERA = re.compile(r'OPR/([6-9][0-9]|[1-9][0-9]{2,})')
EXCLUDE_EDGE_OPERA = re.compile(r'Edg/|OPR/')

def is_modern_browser(user_agent: str) -> bool:
    """Check if the given user agent string belongs to a modern browser."""
    if CHROME.search(user_agent) and not EXCLUDE_EDGE_OPERA.search(user_agent):
        # Chrome 70+ (excluding Edge and Opera)
        return True

    if FIREFOX.search(user_agent):
        # Firefox 60+
        return True

    if SAFARI.search(user_agent) and 'Safari' in user_agent and 'Chrome' not in user_agent:
        # Safari 12+ (excluding Chrome)
        return True

    if EDGE.search(user_agent):
        # Edge (Chromium) 79+
        return True

    if OPERA.search(user_agent):
        # Opera 60+
        return True

    return False

def is_internet_explorer(user_agent: str) -> bool:
    """Check if the given user agent string belongs to Internet Explorer."""
    return (
        'msie' in user_agent.lower() or
        'trident/' in user_agent.lower()
    )
