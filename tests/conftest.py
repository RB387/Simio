from typing import Optional

import pytest
import trafaret as t

from simio.app.builder import AppBuilder
from simio.handler.base import BaseHandler
from simio.handler.utils import route


@pytest.fixture(autouse=True, scope="function")
def clear_globals():
    AppBuilder._APP_ROUTES = []


SampleSchemaOne = t.Dict({
    t.Key("arg_one"): t.String(),
    t.Key("arg_two"): t.Int(),
    t.Key("arg_three", optional=True): t.Bool()
})


SampleSchemaTwo = t.Dict({
    t.Key("arg_one"): t.Dict({
        t.Key("key"): t.List(
            t.Dict({
                t.Key("sub_key"): t.Int(),
                t.Key("sub_key2"): t.String()
            })
        )
    }),
    t.Key("arg_two"): t.List(t.Int()),
})


class SampleHandlerOneRaw(BaseHandler):
    async def post(self, user_id: int, data: SampleSchemaOne):
        return self.response({"user_id": user_id, "data": data.json()})

    async def get(self, user_id: int, q: Optional[str] = None):
        return self.response({"user_id": user_id, "q": q})


@route(path="/v1/hello/{user_id}/")
class SampleHandlerOne(SampleHandlerOneRaw):
    ...


class SampleHandlerTwoRaw(BaseHandler):
    async def get(self, q: Optional[str] = None):
        return self.response({"q": q})


@route(path="/v1/test")
class SampleHandlerTwo(SampleHandlerTwoRaw):
    ...


class SampleHandlerThreeRaw(BaseHandler):
    async def get(self, some_schema: SampleSchemaTwo):
        return self.response({"some_schema": some_schema})


@route(path="/v1/test2")
class SampleHandlerThree(SampleHandlerThreeRaw):
    ...
