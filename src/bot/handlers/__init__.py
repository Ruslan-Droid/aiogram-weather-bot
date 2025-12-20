from .commands import commands_router
from .user_statuses import user_status_router
from .groups import groups_router

__all__ = ["routers", "commands_router", "user_status_router", "groups_router"]

routers = [
    commands_router,
    groups_router,
    user_status_router,
]