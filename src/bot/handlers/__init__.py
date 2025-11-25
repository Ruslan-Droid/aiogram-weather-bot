from .commands import commands_router
from .user_status import user_status_router

__all__ = ["routers"]

routers = [
    commands_router,
    user_status_router,
]
