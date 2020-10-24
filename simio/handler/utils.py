import json
from typing import Any, Type, List, Optional as Opt, Callable, get_type_hints

from aiohttp.web_exceptions import HTTPBadRequest
from pydantic import ValidationError, BaseModel  # pylint: disable=no-name-in-module
from typingplus import cast

from simio.app.builder import AppBuilder
from simio.handler.base import BaseHandler, HandlerMethod
from simio.handler.http_methods import HTTP_METHODS
from simio.utils import is_typing, cast_cap_words_to_lower


def route(path: str, name: Opt[str] = None) -> Callable:  # pylint: disable=unused-argument
    """
        Decorator to add app route

        Usage:
            >>> @route('/v1/hello/')
            >>> class SomeHandler(BaseHandler):

    :param path: http path of route
    :param name: Optional. Name of your handler
    """

    def decorator(cls: Type[BaseHandler]) -> Callable:
        nonlocal name

        if name is None:
            name = cast_cap_words_to_lower(cls.__name__)

        AppBuilder.add_route(path=path, handler=cls, name=name)
        handler_methods = _prepare_handler_method(cls, path)

        cls.handler_methods = handler_methods

        def wrapper(*args, **kwargs) -> BaseHandler:
            return cls(*args, **kwargs)

        return wrapper

    return decorator


def get_bad_request_exception(message: Any) -> HTTPBadRequest:
    """
    :param message: text of your exception
    :return: returns HTTPBadRequest exception with json:
            {"error": message}
    """
    body = {"error": message}
    return HTTPBadRequest(reason="Bad Request", body=json.dumps(body))


def _handler(func: Callable):
    """
        Decorator that collects data from request and adds them to function kwargs

    :param func: request handler
    """

    async def wrapper(self: BaseHandler, *args, **kwargs) -> Any:
        function_kwargs = get_type_hints(func)
        for arg_name, type_hint in function_kwargs.items():
            if not is_typing(type_hint) and issubclass(type_hint, BaseModel):
                value = await _cast_model_type(self, type_hint)
            else:
                value = _cast_type(self, arg_name, type_hint)

            if value is not None:
                kwargs[arg_name] = value

        return await func(self, *args, **kwargs)

    return wrapper


async def _cast_model_type(self, model_type):
    """
        Casting response json to Model from pydantic
    """
    try:
        request_json = await self.request.json()
        value = model_type(**request_json)
        return value
    except ValidationError as e:
        raise get_bad_request_exception(e.json())
    except json.decoder.JSONDecodeError as e:
        raise get_bad_request_exception(str(e))


def _cast_type(self, arg_name, type_hint):
    """
        Casting data from url
    """
    value = self.request.match_info.get(arg_name)
    value = value or self.request.query.get(arg_name)
    try:
        return cast(type_hint, value)
    except (ValueError, TypeError):
        raise get_bad_request_exception(f"{arg_name}: Not valid {type_hint} value")


def _prepare_handler_method(cls: Type[BaseHandler], path: str) -> List[HandlerMethod]:
    """
        Extracts from class all request handlers by http methods name,
        setups handler_method property of class and adds decorator _handler.
    """
    handler_methods_name = HTTP_METHODS.intersection(set(dir(cls)))
    handler_methods = []

    for method_name in handler_methods_name:
        handler = getattr(cls, method_name)
        handler_method = HandlerMethod(method=method_name)
        method_args = get_type_hints(handler)

        for arg_name, type_hint in method_args.items():
            if not is_typing(type_hint) and issubclass(type_hint, BaseModel):
                handler_method.request_schema = type_hint
            elif f"{{{arg_name}}}" in path:
                handler_method.path_args[arg_name] = type_hint
            else:
                handler_method.query_args[arg_name] = type_hint

        handler_methods.append(handler_method)
        setattr(cls, method_name, _handler(handler))

    return handler_methods
