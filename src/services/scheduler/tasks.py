from src.services.scheduler.taskiq_broker import broker


@broker.task
async def test():
    print()
    print("Это простая задача без расписания")
    print()


@broker.task
async def test_with_arguments(value: int) -> int:
    print()
    print("Задача с аргументом")
    print(value, value + 10)
    return value + 10
