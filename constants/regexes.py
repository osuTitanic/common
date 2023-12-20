
import re

OSU_VERSION = re.compile(
    r"^b(?P<date>\d{1,8})"
    r"(?:(?P<name>(?!dev|tourney|test|peppy|arcade|ubertest\b)\w+\b))?"
    r"(?:\.(?P<revision>\d{1,2}|))?"
    r"(?P<stream>dev|tourney|test|peppy|arcade|ubertest)?$"
)

EMAIL = re.compile(
    r"^[^@\s]{1,200}@[^@\s\.]{1,30}(?:\.[^@\.\s]{2,24})+$"
)

USERNAME = re.compile(
    r'^[a-zA-Z0-9|^\-{}_|\[\] ぁ-んァ-ン]+$'
)
