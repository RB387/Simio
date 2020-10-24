import asyncio
from typing import Optional

import pytest
from pydantic import BaseModel

from simio.app.builder import AppBuilder
from simio.handler.base import BaseHandler
from simio.handler.utils import route


@pytest.fixture(autouse=True, scope="function")
def clear_globals():
    AppBuilder._APP_ROUTES = []


class SampleModelOne(BaseModel):
    arg_one: str
    arg_two: int
    arg_three: Optional[bool] = False


class SampleHandlerOneRaw(BaseHandler):
    async def post(self, user_id: int, data: SampleModelOne):
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
