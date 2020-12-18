import asyncio
from unittest.mock import Mock

import pytest

from simio.app.directors.crons import AsyncCronsDirector
from simio.app.directors.workers import AsyncWorkersDirector
from simio.app.utils import deep_merge_dicts
from simio.app.config_names import CLIENTS, DIRECTORS
from simio.app.default_config import get_default_config
from tests.test_unit.test_app.conftest import TEST_APP_CONFIG, example_cron


@pytest.mark.parametrize(
    "lhs, rhs, expected_result",
    (
        (
            {"key": {"key1": 2, "key2": 3,}, "key1": 1},
            {"key": {"key1": 0, "key3": 4}, "key1": 2, "key2": 3,},
            {"key": {"key1": 0, "key2": 3, "key3": 4,}, "key1": 2, "key2": 3,},
        ),
    ),
)
def test_merge_configs(lhs, rhs, expected_result):
    result = deep_merge_dicts(lhs, rhs)
    assert result == expected_result


class TestAppBuilder:
    def test_initiated_app_config(self, app):
        assert app.app["config"] == deep_merge_dicts(
            get_default_config(), TEST_APP_CONFIG
        )

    def test_created_clients(self, app):
        assert len(app.app[CLIENTS]) == len(TEST_APP_CONFIG[CLIENTS])

        for client, client_instance in app.app[CLIENTS].items():
            for attr_name, attr_value in TEST_APP_CONFIG[CLIENTS][client].items():
                assert getattr(client_instance, attr_name) == attr_value

    @pytest.mark.asyncio
    async def test_created_workers(self, app):
        workers = TEST_APP_CONFIG[DIRECTORS][AsyncWorkersDirector]
        tasks = app.app[DIRECTORS][AsyncWorkersDirector]._worker_tasks
        assert len(tasks) == len(TEST_APP_CONFIG[DIRECTORS][AsyncWorkersDirector])

        for worker, worker_instance in tasks.items():
            result = await asyncio.gather(worker_instance)
            assert result[0] == workers[worker]["return_value"]

    @pytest.mark.asyncio
    async def test_created_cron(self, app):
        crons = app[DIRECTORS][AsyncCronsDirector]._crons
        assert len(crons) == len(
            TEST_APP_CONFIG[DIRECTORS][AsyncCronsDirector]["*/1 * * * *"]
        )
        cron = app[DIRECTORS][AsyncCronsDirector][example_cron]

        await cron.next()
        app.app[CLIENTS][Mock].check.assert_called_with(alive=True)
