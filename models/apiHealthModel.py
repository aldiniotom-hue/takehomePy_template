from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class APIHealthTestModel(Base):
    __tablename__ = "APIHealthTest"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    message: Mapped[str] = mapped_column(String(100), nullable=True)
