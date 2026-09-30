import uuid
from datetime import date

from sqlalchemy import Date, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("first_name", "last_name", name="uq_users_full_name"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    first_name: Mapped[str] = mapped_column(String(32), nullable=False)
    last_name: Mapped[str] = mapped_column(String(32), nullable=False)
    last_access: Mapped[date] = mapped_column(Date, nullable=False)
    use_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)