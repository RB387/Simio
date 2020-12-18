__doc__ = "Module with base entities for Handler"

import json
from typing import Any, Optional as Opt, List, Type, Callable

from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest

from simio.handler.entities import HandlerMethod
from simio.handler.request_validator import AbstractRequestValidator, RequestValidator


def get_bad_request_exception(message: Any) -> HTTPBadRequest:
    """
    :param message: text of your exception
    :return: returns HTTPBadRequest exception with json:
            {"error": message}
    """
    body = {"error": message}
    return HTTPBadRequest(reason="Bad Request", body=json.dumps(body).encode())


class BaseHandler(web.View):
    """
        Use this class to create your own handlers


        Has some useful properties:
            self.app -- get your application
            self.config -- get config of your application
            await self.request_json -- get json of request

        And methods:
            self.response(body, status, **kwargs) -- get json web.Response

        `handler_methods` is property only for framework. Don't change value of this
        `request_validator_cls` is class that will validate incoming request.
                                You can write your own validator
                                with AbstractRequestValidator interface
        `on_exception_response` is function that receives exception message (str) and
                                returns HTTPBadRequest.
                                This function will be passed to request_validator_cls

    """

    handler_methods: Opt[List[HandlerMethod]] = None
    request_validator_cls: Type[AbstractRequestValidator] = RequestValidator
    on_exception_response: Callable[[Any], HTTPBadRequest] = get_bad_request_exception

    @property
    def app(self) -> web.Application:
        return self.request.app

    @property
    def config(self) -> dict:
        return self.app["config"]

    @property
    async def request_json(self) -> dict:
        return await self.request.json()

    @staticmethod
    def response(body: Any, status: int = 200, **kwargs) -> web.Response:
        return web.json_response(body, status=status, **kwargs)
