from abc import ABC, abstractmethod
from typing import Any

from simio.app.app import Application


class AbstractDirector(ABC):
    """
    Abstract class for director's interface
    """

    def __init__(self, config: Any):
        self.config = config

    @abstractmethod
    async def start(self, app: Application):
        """
        Setup and run everything you need
        """
        ...

    @abstractmethod
    async def stop(self, app: Application):
        """
        Stop and cleanup your tasks
        """
        ...
