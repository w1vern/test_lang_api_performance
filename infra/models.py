
from uuid import UUID

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

class Base(DeclarativeBase):
    pass

class Data(Base):
    __tablename__ = "data"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    field1: Mapped[str]
    field2: Mapped[int]

class Time(Base):
    __tablename__ = "times"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    time: Mapped[float]
    lang_code: Mapped[str]
