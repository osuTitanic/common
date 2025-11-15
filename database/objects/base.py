
from sqlalchemy.orm import declarative_base

Base = declarative_base()
Base.__allow_unmapped__ = True
