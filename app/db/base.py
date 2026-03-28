from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# import models so Alembic can discover tables from Base.metadata

from app.db import models


