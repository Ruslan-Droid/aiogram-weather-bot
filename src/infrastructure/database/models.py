from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Float, ForeignKey
from src.infrastructure.database.db import Base
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"


class UserModel(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True
    )
    username: Mapped[str | None] = mapped_column(String(32))
    first_name: Mapped[str | None] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))
    language_code: Mapped[str | None] = mapped_column(String(10), default="ru")
    # Timezone region name (e.g., 'Europe/Moscow')
    tz_region: Mapped[str | None] = mapped_column(String(50))
    # Manual timezone offset in the format '+03:00' or '-05:00'
    tz_offset: Mapped[str | None] = mapped_column(String(50))

    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    city: Mapped[str | None] = mapped_column(String(100))

    role: Mapped[UserRole] = mapped_column(PgEnum(UserRole, name="user_role"), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_banned: Mapped[bool] = mapped_column(default=False)

    user_schedule_task: Mapped["UserScheduleTask"] = relationship(
        "UserScheduleTask",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )

    def __repr__(self):
        return (f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}', "
                f"lang='{self.language_code}', coords='{self.latitude}, {self.longitude}'>')>")


class UserScheduleTask(Base):
    __tablename__ = "user_schedule_task"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        unique=True,
        nullable=False)

    notifications_enabled: Mapped[bool] = mapped_column(default=False)
    notification_time: Mapped[str] = mapped_column(String(5), default="09:00")
    taskiq_task_id: Mapped[str | None] = mapped_column(String(100))
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="user_schedule_task")
