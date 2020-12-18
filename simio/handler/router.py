from typing import Any, Type, List, Optional as Opt, Callable, get_type_hints

from trafaret import Trafaret

from simio.app.builder import AppBuilder
from simio.handler.base import BaseHandler
from simio.handler.entities import RequestSchema, HandlerMethod
from simio.handler.http_methods import HTTP_METHODS
from simio.handler.request_validator import AbstractRequestValidator
from simio.utils import is_typing, cast_cap_words_to_lower


def route(
    path: str, name: Opt[str] = None  # pylint: disable=unused-argument
) -> Callable:
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
        handler_methods = _prepare_handler_methods(cls, path)

        cls.handler_methods = handler_methods

        def wrapper(*args, **kwargs) -> BaseHandler:
            return cls(*args, **kwargs)

        return wrapper

    return decorator


def _prepare_handler_methods(cls: Type[BaseHandler], path: str) -> List[HandlerMethod]:
    """
        Extracts from class all request handlers by http methods name,
        setups handler_method property of class and adds decorator _handler.
    """
    handler_methods_name = HTTP_METHODS.intersection(set(dir(cls)))
    handler_methods = []

    for method_name in handler_methods_name:
        handler = getattr(cls, method_name)

        handler_method = _create_handler_method(handler, method_name, path)
        request_validator = cls.request_validator_cls(
            handler_method=handler_method,
            on_exception_response=cls.on_exception_response,
        )

        handler_methods.append(handler_method)
        setattr(cls, method_name, _handler(handler, request_validator))

    return handler_methods


def _create_handler_method(handler: Callable, method_name: str, path: str):
    handler_method = HandlerMethod(method=method_name)
    method_args = get_type_hints(handler)
    method_args.pop("return", None)

    for arg_name, type_hint in method_args.items():
        if not is_typing(type_hint) and isinstance(type_hint, Trafaret):
            handler_method.request_schema = RequestSchema(
                trafaret=type_hint, name=arg_name
            )
        elif f"{{{arg_name}}}" in path:
            handler_method.path_args[arg_name] = type_hint
        else:
            handler_method.query_args[arg_name] = type_hint

    return handler_method


def _handler(func: Callable, request_validator: AbstractRequestValidator):
    """
    Decorator that collects data from request and adds them to function kwargs

    :param func: request handler
    """

    async def wrapper(self: BaseHandler, *args, **kwargs) -> Any:
        validated_request_data = await request_validator.validate(self.request)
        kwargs.update(**validated_request_data)
        return await func(self, *args, **kwargs)

    return wrapper
