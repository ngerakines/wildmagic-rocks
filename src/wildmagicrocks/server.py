import os
import logging
from typing import Optional, Set, Union
import jinja2
from aiohttp import web
import aiohttp_jinja2
import numpy as np

from wildmagicrocks.model import random_surges


logger = logging.getLogger(__name__)


def int_or(value: Optional[Union[str, int]], default_value: int) -> int:
    if value is not None:
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
        elif isinstance(value, int):
            return value
    return default_value


async def handle_index(request):
    rng = np.random.default_rng()
    surges = random_surges(rng)
    return aiohttp_jinja2.render_template("index.html", request, context={"surge": surges[0]})


async def handle_table(request):
    rng = np.random.default_rng()

    count = int_or(request.query.get("count"), 20)
    surges = random_surges(rng, count)

    return aiohttp_jinja2.render_template("table.html", request, context={"surges": surges})


def template_location() -> str:
    return os.path.join(os.getcwd(), "templates")


def static_location() -> str:
    return os.path.join(os.getcwd(), "static")


async def start_web_server():
    app = web.Application()

    app.add_routes([web.static("/static", static_location(), append_version=True)])
    app.add_routes([web.get("/", handle_index)])
    app.add_routes([web.get("/table", handle_table)])

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_location()))

    return app
