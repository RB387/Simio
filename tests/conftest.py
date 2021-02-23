from unittest.mock import Mock

import pytest
from aiohttp import web

from simio import AppConfig, AppBuilder

TEST_APP_CONFIG = {
    AppConfig: {
        AppConfig.name: "example_project",
        AppConfig.enable_swagger: False,
        AppConfig.app_path: "tests",
    },
    Mock: {"host": "localhost", "port": 27017},
    "return_value": 5,
}

builder = AppBuilder(TEST_APP_CONFIG)


@pytest.fixture()
def builder_injector():
    return builder._injector


@pytest.fixture()
@pytest.mark.asyncio
async def app(loop):
    app = builder.build_app()
    app.app.freeze()
    await app.app.startup()

    yield app

    await app.app.shutdown()
