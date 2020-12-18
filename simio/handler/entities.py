from dataclasses import dataclass, field
from typing import Optional as Opt

from trafaret import Trafaret


@dataclass
class RequestSchema:
    trafaret: Trafaret
    name: str


@dataclass
class HandlerMethod:
    """
        Describes HTTP method of BaseHandler

        path_args and query_args contains dict where
        keys are names of args and value are type hints
    """

    method: str

    request_schema: Opt[RequestSchema] = None
    path_args: dict = field(default_factory=dict)
    query_args: dict = field(default_factory=dict)
