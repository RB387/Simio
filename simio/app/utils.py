import asyncio
import glob
from runpy import run_path

from aiohttp import web

from simio.app.config_names import DIRECTORS


async def directors_shutdown(app: web.Application):
    tasks = []

    for director in app.get(DIRECTORS, {}).values():
        tasks.append(director.stop())

    await asyncio.gather(*tasks)


def initialize_all_modules(handlers_path):
    """
    Runs all modules to execute decorators and register routes
    """
    for filepath in glob.iglob(f"{handlers_path}/**/*.py", recursive=True):
        run_path(filepath)


def deep_merge_dicts(lhs: dict, rhs: dict) -> dict:
    """
    Deep merging two dicts
    """
    for key, value in rhs.items():
        if isinstance(value, dict):
            node = lhs.setdefault(key, {})
            deep_merge_dicts(node, value)
        else:
            lhs[key] = value

    return lhs
