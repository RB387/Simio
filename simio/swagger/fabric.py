from typing import List, Type, Union

from aiohttp.web_exceptions import HTTPBadRequest

from simio.app.config_names import APP
from simio.app.entities import AppRoute
from simio.exceptions import UnsupportedSwaggerType
from simio.swagger.entities import (
    SwaggerConfig,
    SwaggerInfo,
    SwaggerPath,
    SwaggerMethod,
    SwaggerResponse,
    SwaggerSchema,
    SwaggerProperty,
    SwaggerParameter,
)
from simio.swagger.type_mapping import PYTHON_TYPE_TO_SWAGGER
from simio.handler.base import HandlerMethod
from simio.utils import is_typing


def _cast_to_swagger_type(var_type: Union[Type]):
    if is_typing(var_type):
        var_type = var_type.__args__[0]

    if var_type not in PYTHON_TYPE_TO_SWAGGER:
        raise UnsupportedSwaggerType(
            f"Handler argument with type {var_type} is not supported with swagger"
        )

    return PYTHON_TYPE_TO_SWAGGER[var_type]


def swagger_fabric(app_config: dict, app_routes: List[AppRoute]) -> SwaggerConfig:
    """
        Function to generate swagger config for application

    :param app_config: config[APP]
    :param app_routes: App routes
    :return: SwaggerConfig object
    """
    swagger = SwaggerConfig(
        info=SwaggerInfo(version=app_config[APP.version], title=app_config[APP.name],),
    )

    for route in app_routes:
        path = SwaggerPath(path=route.path,)

        if route.handler.handler_methods is None:
            continue

        for handler_method in route.handler.handler_methods:
            method = _create_swagger_method(handler_method, route)
            path.methods.append(method)

        swagger.paths.append(path)

    return swagger


def _create_swagger_method(
    handler_method: HandlerMethod, route: AppRoute
) -> SwaggerMethod:
    method = SwaggerMethod(
        tags=[route.name],
        method=handler_method.method,
        responses=[
            SwaggerResponse(code=200, description="Successful request"),
            SwaggerResponse(
                code=HTTPBadRequest.status_code, description="Invalid input"
            ),
        ],
    )

    schema = SwaggerSchema(type="object")

    if handler_method.request_schema:
        schema_name = handler_method.request_schema.__name__
        for field_name, field in handler_method.request_schema.__fields__.items():
            schema.properties.append(
                SwaggerProperty(
                    name=field_name, type=_cast_to_swagger_type(field.type_)
                )
            )
        method.parameters.append(
            SwaggerParameter(in_="body", name=schema_name, schema=schema,)
        )

    for query_arg_name, url_arg_type in handler_method.query_args.items():
        method.parameters.append(
            SwaggerParameter(
                in_="query",
                name=query_arg_name,
                type=_cast_to_swagger_type(url_arg_type),
            )
        )

    for path_arg_name, path_arg_type in handler_method.path_args.items():
        method.parameters.append(
            SwaggerParameter(
                in_="path",
                name=path_arg_name,
                type=_cast_to_swagger_type(path_arg_type),
                required=True,
            )
        )

    return method
