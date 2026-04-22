from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy.orm import DeclarativeBase


def utcnow() -> datetime:
    return datetime.utcnow()


def new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass
