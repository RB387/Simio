import asyncio
from asyncio import Task
from typing import Dict, Callable, Any, Awaitable

from simio.app.app import Application
from simio.app.directors.abstract import AbstractDirector
from simio.exceptions import WorkerTypeError

WorkerConfig = Dict[str, Any]


class AsyncWorkersDirector(AbstractDirector):
    """Director for workers"""

    def __init__(self, config: Dict[Callable, WorkerConfig]):
        super().__init__(config)
        self._worker_tasks: Dict[Callable, Task] = {}

    def __getitem__(self, item):
        return self._worker_tasks[item]

    async def start(self, app: Application):
        for worker_func, config in self.config.items():
            worker = worker_func(app=app, **config)
            if not isinstance(  # pylint: disable=isinstance-second-argument-not-valid-type
                worker, Awaitable
            ):
                raise WorkerTypeError(
                    "You are trying to create worker that is not async!"
                )

            task = asyncio.create_task(worker)
            self._worker_tasks[worker_func] = task

    async def stop(self, app: Application):
        tasks = []

        for task in self._worker_tasks.values():
            task.cancel()
            tasks.append(task)

        await asyncio.gather(*tasks)
