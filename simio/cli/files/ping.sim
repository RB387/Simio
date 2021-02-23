from asyncio import sleep

from simio import web
from simio.job import async_worker
from simio_di import Var


@async_worker.register()
async def ping_worker(app: web.Application, sleep_time: Var["sleep_time"]):
    while True:
        app.logger.info("Background worker works!")
        await sleep(sleep_time)
