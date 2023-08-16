
import re

OSU_VERSION = re.compile(
    r"^b(?P<date>\d{1,8})"
    r"(?:(?P<name>(?!dev|tourney|test|peppy\b)\w+\b))?"
    r"(?:\.(?P<revision>\d{1,2}|))?"
    r"(?P<stream>dev|tourney|test|peppy)?$"
)
