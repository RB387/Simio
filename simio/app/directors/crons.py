import asyncio
from typing import Dict, Iterable, Callable, Awaitable

from aiocron import Cron, crontab
from aiohttp import web
from croniter import croniter

from simio.app.app import Application
from simio.app.config_names import APP
from simio.app.directors.abstract import AbstractDirector
from simio.exceptions import InvalidCronFormat

CronSchedule = str
CronsConfig = Dict[CronSchedule, Iterable[Callable]]


class AsyncCronsDirector(AbstractDirector):
    """Director for cron"""

    def __init__(self, config: CronsConfig):
        super().__init__(config)
        self._crons: Dict[Callable, Cron] = {}

    def __getitem__(self, item):
        return self._crons[item]

    async def start(self, app: Application):
        for cron_schedule, cron_jobs in self.config.items():
            for cron_job_func in cron_jobs:
                cron = await self.create_cron(app, cron_schedule, cron_job_func)
                self._crons[cron_job_func] = cron

    async def stop(self, app: Application):
        tasks = []

        for cron in self._crons.values():
            cron.handle.cancel()
            tasks.append(cron.handle)

        await asyncio.gather(*tasks)

    @staticmethod
    async def create_cron(
        app: Application,
        cron: str,
        cron_job_func: Callable[[web.Application], Awaitable],
    ):
        if not croniter.is_valid(cron):
            raise InvalidCronFormat(f"Cron {cron} has invalid format")

        return crontab(
            cron, cron_job_func, args=(app,), tz=app["config"][APP][APP.timezone]
        )
