from src.services.scheduler.taskiq_broker import broker


@broker.task(task_name="Simple task")
async def simple_task():
    print("Simple task")
