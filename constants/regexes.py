
import re

OSU_VERSION = re.compile(
    r"^b(?P<date>\d{1,8})"
    r"(?:(?P<name>\w+\b))?"
    r"(?:\.(?P<revision>\d{1,2}|))?"
    r"(?P<stream>\w+)?$"
)

EMAIL = re.compile(
    r"^[^@\s]{1,200}@[^@\s\.]{1,30}(?:\.[^@\.\s]{2,24})+$"
)

USERNAME = re.compile(
    r'^[a-zA-Z0-9^\-{}_\[\] ]+$'
)

DISCORD_USERNAME = re.compile(
    r'^@?(?!.*?\.{2,})[a-z0-9_\.]{2,32}$'
)

DISCORD_EMOTE = re.compile(
    r'<a?:([a-zA-Z0-9_]{2,32}):\d{17,20}>'
)

URL = re.compile(
    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
)

MARKDOWN_LINK = re.compile(
    r"\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)"
)

OSU_USER_AGENT = re.compile(
    r"^osu!*|Mozilla/\d+\.\d+ \(compatible; Clever Internet Suite \d+\.\d+\)$"
)

OSU_CHAT_LINK_MODERN = re.compile(
    r"\[((?:https?:\/\/)[^\s\]]+)\s+(.+?)\]"
)

OSU_CHAT_LINK_LEGACY = re.compile(
    r"\[([^\]]+)\]\((https?:\/\/[^)]+)\)"
)

# Regex to match filter patterns: field(operator)value
# Supports =, >=, <=, >, <
# Values can be quoted strings or unquoted
FILTER_PATTERN = re.compile(
    r'(\w+)(>=|<=|>|<|=)(?:"([^"]+)"|(\S+))'
)
