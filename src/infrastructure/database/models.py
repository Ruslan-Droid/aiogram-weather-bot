from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Float, Integer, Enum
from src.infrastructure.database.database import Base
from src.bot.enums.roles import UserRole


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True
    )
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        default="ru"
    )
    # Timezone region name (e.g., 'Europe/Moscow')
    tz_region: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Manual timezone offset in the format '+03:00' or '-05:00'
    tz_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    weather_alerts: Mapped[bool] = mapped_column(default=True)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_banned: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return (f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}', "
                f"lang='{self.language_code}', coords='{self.latitude}, {self.longitude}'>')>")
