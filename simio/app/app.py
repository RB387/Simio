from asyncio import AbstractEventLoop
from typing import Callable, Type, Any, Awaitable, Iterator

from aiohttp import web
from aiohttp.web_runner import BaseSite


class Application:
    """
    Abstraction for simio's application
    """

    def __init__(
        self,
        app: web.Application,
        loop: AbstractEventLoop,
        aiohttp_site_cls: Type[BaseSite],
        **app_runner_config,
    ):
        """
        You can modify aiohttp's AppRunner with app_runner_config
        app_runner_config is passing to AppRunner constructor

        aiohttp_site_cls is aiohttp's site class that will start app
        Read aiohttp docs for more info

        Also custom event loop can be chosen. Pass it in builder.
        """
        self._app = app
        self._loop = loop
        self._runner = web.AppRunner(self._app, **app_runner_config)
        self._aiohttp_site_cls = aiohttp_site_cls

    def __getitem__(self, key: str) -> Any:
        return self._app[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._app[key] = value

    def __delitem__(self, key: str) -> None:
        del self._app[key]

    def __len__(self) -> int:
        return len(self._app)

    def __iter__(self) -> Iterator[str]:
        return iter(self._app)

    @property
    def app(self):
        return self._app

    @property
    def app_runner(self):
        return self._runner

    def run(
        self,
        run_forever: bool = True,
        log_func: Callable[..., None] = print,
        **site_kwargs,
    ):
        """
        Runs aiohttp's application

        All BaseSites's parameters can be passed in kwargs
        such as host, port and other

        log_func is function that will print info about app start

        If run_forever is true, then this method will block execution
        """
        self._loop.run_until_complete(self._runner.setup())
        site = self._aiohttp_site_cls(runner=self._runner, **site_kwargs)
        self._loop.run_until_complete(site.start())

        log_func(f"======== Running on {site.name} ========\n(Press CTRL+C to quit)")
        if run_forever:
            self._loop.run_forever()

    def add_startup(self, *startup_funcs: Callable[[Any], Awaitable]):
        self._app.on_startup.append(*startup_funcs)

    def add_cleanup(self, *cleanup_funcs: Callable[[Any], Awaitable]):
        self._app.on_cleanup.append(*cleanup_funcs)

    def add_shutdown(self, *shutdown_funcs: Callable[[Any], Awaitable]):
        self._app.on_shutdown.append(*shutdown_funcs)
