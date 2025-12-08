from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, Float, ForeignKey, Boolean, JSON, UniqueConstraint, Index, Integer
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
    role: Mapped[UserRole] = mapped_column(PgEnum(UserRole, name="user_role"), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_banned: Mapped[bool] = mapped_column(default=False)
    # Timezone region name (e.g., 'Europe/Moscow')
    tz_region: Mapped[str | None] = mapped_column(String(50))

    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    city: Mapped[str | None] = mapped_column(String(100))

    daily_task: Mapped["DailyUserTaskModel"] = relationship(
        "DailyUserTaskModel",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    admin_group_associations: Mapped[list["GroupAdminModel"]] = relationship(
        "GroupAdminModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Свойство для удобного доступа к группам пользователя
    @property
    def admin_groups(self) -> list["GroupModel"]:
        return [assoc.group for assoc in self.admin_group_associations if assoc.is_active]


class DailyUserTaskModel(Base):
    __tablename__ = "user_schedule_task"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False)
    notifications_enabled: Mapped[bool] = mapped_column(default=False)
    notification_time: Mapped[str] = mapped_column(String(5), default="09:00")
    taskiq_task_id: Mapped[str | None] = mapped_column(String(100))

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="daily_task")


class GroupModel(Base):
    __tablename__ = "groups"

    group_telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True
    )
    title: Mapped[str | None] = mapped_column(String(255))
    chat_type: Mapped[str] = mapped_column(String(20))  # group, supergroup, channel
    added_by_telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL")
    )
    bot_status: Mapped[str] = mapped_column(String(20))  # member, administrator, restricted, left, kicked
    admin_permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    admin_user_associations: Mapped[list["GroupAdminModel"]] = relationship(
        "GroupAdminModel",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Свойство для удобного доступа к админам группы
    @property
    def admins(self) -> list["UserModel"]:
        return [assoc.user for assoc in self.admin_user_associations if assoc.is_active]


class GroupAdminModel(Base):
    __tablename__ = "group_admins"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    admin_permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="admin_group_associations")
    group: Mapped["GroupModel"] = relationship("GroupModel", back_populates="admin_user_associations")

    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='uq_user_group_admin'),
        Index('idx_group_admin_user_id', 'user_id'),
        Index('idx_group_admin_group_id', 'group_id')
    )
