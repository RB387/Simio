from typing import Optional
from unittest.mock import Mock

import trafaret as t
from aiohttp import web
from simio_di import Var, Depends

from simio import R, router
from simio.job import async_worker, async_cron

SampleSchemaOne = t.Dict(
    {
        t.Key("arg_one"): t.String(),
        t.Key("arg_two"): t.Int(),
        t.Key("arg_three", optional=True): t.Bool(),
    }
)
SampleSchemaTwo = t.Dict(
    {
        t.Key("arg_one"): t.Dict(
            {
                t.Key("key"): t.List(
                    t.Dict({t.Key("sub_key"): t.Int(), t.Key("sub_key2"): t.String()})
                )
            }
        ),
        t.Key("arg_two"): t.List(t.Int()),
        t.Key("arg_three"): t.List(t.List(t.Int())),
    }
)


@router.post("/v1/hello/{user_id}/")
async def sample_handler_post(
    user_id: R[int], query: R[int], data: R[SampleSchemaOne], mock: Depends[Mock]
):
    mock.handler(injected=True)
    return web.json_response({"user_id": user_id, "data": data, "q": query})


@router.get("/v1/hello/{user_id}/")
async def sample_handler_get(user_id: R[int], q: R[Optional[str]] = None):
    return web.json_response({"user_id": user_id, "q": q})


@router.get("/v1/test")
async def sample_handler_two_get(q: R[str] = None):
    return web.json_response({"q": q})


@router.get(path="/v1/test2")
async def sample_handler_three_get(some_schema: R[SampleSchemaTwo]):
    return web.json_response({"some_schema": some_schema})


@async_worker.register()
async def example_worker(app: web.Application, return_value: Var["return_value"]):
    return return_value


@async_cron.register(cron="*/1 * * * *")
async def example_cron(app, mock: Depends[Mock]):
    mock.check(alive=True)
