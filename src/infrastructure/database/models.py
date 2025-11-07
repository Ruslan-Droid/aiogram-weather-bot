from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Float
from src.infrastructure.database.db import Base
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
import enum


class UserRole(enum.Enum):
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
    weather_alerts: Mapped[bool] = mapped_column(default=True)

    role: Mapped[UserRole] = mapped_column(PgEnum(UserRole, name="user_role"), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_banned: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return (f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}', "
                f"lang='{self.language_code}', coords='{self.latitude}, {self.longitude}'>')>")
