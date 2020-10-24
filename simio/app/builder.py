import asyncio
import glob
import json
from runpy import run_path
from typing import Type, Awaitable, Callable, Any, List

from aiohttp import web
from swagger_ui import aiohttp_api_doc

from simio.app.entities import AppRoute
from simio.app.default_config import get_default_config
from simio.clients.client_protocol import ClientProtocol
from simio.app.config_names import CLIENTS, WORKERS, APP
from simio.exceptions import WorkerTypeError
from simio.handler.base import BaseHandler
from simio.swagger.fabric import swagger_fabric
from simio.swagger.entities import SwaggerConfig


def _initialize_all_modules():
    """
    Runs all modules to execute decorators and register routes
    """
    not_to_run = (
        "python3.",
        "setup.py",
    )
    for filepath in glob.iglob("**/*.py", recursive=True):
        run = True

        for not_to_run_file in not_to_run:
            if not_to_run_file in filepath:
                run = False
                break

        if run:
            run_path(filepath)


def _deep_merge_dicts(lhs: dict, rhs: dict) -> dict:
    """
    Deep merging two dicts
    """
    for key, value in rhs.items():
        if isinstance(value, dict):
            node = lhs.setdefault(key, {})
            _deep_merge_dicts(node, value)
        else:
            lhs[key] = value

    return lhs


class AppBuilder:
    """
        Class to build your application

        Can be used only for one application because of global _APP_ROUTES property
    """

    _APP_ROUTES: List[AppRoute] = []

    def __init__(self, config=None, loop=None):
        default_config = get_default_config()

        if config is None:
            config = {}

        self._config = _deep_merge_dicts(default_config, config)

        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop

        _initialize_all_modules()

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @staticmethod
    def get_app_routes():
        return AppBuilder._APP_ROUTES

    def build_app(self) -> web.Application:
        """
        Use this method to your application

        Adds routes, registers clients and workers, generating swagger

        :return: aiohttp Application
        """
        app = web.Application()
        app["config"] = self._config
        app.add_routes(self._get_routes())

        self._register_clients(app)
        self._create_workers(app)

        if self._config[APP][APP.enable_swagger]:
            if self._config[APP][APP.autogen_swagger]:
                self._generate_swagger()

            aiohttp_api_doc(app, **self._config[APP][APP.swagger_config])

        return app

    def create_worker(
        self,
        app: web.Application,
        worker_func: Callable[[Any], Awaitable],
        **kwargs: dict,
    ):
        """
        Creates workers for application
        :param app: aiohttp Application
        :param worker_func: worker that should be executed
        :param kwargs: kwargs for worker
        :return:
        """
        worker = worker_func(**kwargs)

        if not isinstance(worker, Awaitable):  # pylint: disable=isinstance-second-argument-not-valid-type
            raise WorkerTypeError("You are trying to create worker that is not async!")

        app[WORKERS][worker_func] = self._loop.create_task(worker)

    @staticmethod
    def add_route(path: str, handler: Type[BaseHandler], name: str) -> AppRoute:
        """
        Add route to builder

        :param path: path to handler
        :param handler: handler
        :param name: name of handler
        :return:
        """
        route = AppRoute(handler=handler, path=path, name=name)
        AppBuilder._APP_ROUTES.append(route)
        return route

    @staticmethod
    def _get_routes() -> List[web.RouteDef]:
        """
        Get aiohttp routes from builder routes
        :return: List[web.RouteDef]
        """
        routes = []

        for app_route in AppBuilder.get_app_routes():
            routes.append(app_route.get_route_def())

        return routes

    def _get_clients(self) -> List[Type[ClientProtocol]]:
        """
        Get clients from config
        :return: List[Type[ClientProtocol]]
        """
        return self._config.get(CLIENTS, [])

    def _register_clients(self, app: web.Application):
        """
        Register clients in app
        :param app: aiohttp application
        """
        app[CLIENTS] = {}
        for client in self._get_clients():
            client_kwargs = self._config[CLIENTS][client]
            app[CLIENTS][client] = client(**client_kwargs)

    def _create_workers(self, app: web.Application):
        """
        Create worker for application
        :param app: aiohttp application
        """
        app[WORKERS] = {}
        for worker_func, kwargs in self._config.get(WORKERS, {}).items():
            self.create_worker(app, worker_func, **kwargs)

    def _generate_swagger(self) -> SwaggerConfig:
        """
        Generates and saves swagger to json file
        :return: SwaggerConfig object
        """
        swagger = swagger_fabric(self._config[APP], self.get_app_routes())
        self._save_swagger(swagger)

        return swagger

    def _save_swagger(self, swagger: SwaggerConfig):
        """
        Writes SwaggerConfig object to json file
        :param swagger: SwaggerConfig object
        """
        path = self._config[APP][APP.swagger_config]["config_path"]

        with open(path, "w") as f:
            f.write(json.dumps(swagger.json()))