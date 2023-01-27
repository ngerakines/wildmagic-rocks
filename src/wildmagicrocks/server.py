import os
import logging
from typing import Optional, Set, Union
import jinja2
from aiohttp import web
import aiohttp_jinja2
import numpy as np

from wildmagicrocks.model import SURGES


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
    surge = rng.choice(SURGES)
    the_surge = surge.render(rng)
    return aiohttp_jinja2.render_template("index.html", request, context={"surge": the_surge})


async def handle_table(request):
    rng = np.random.default_rng()

    count = int_or(request.query.get("count"), 20)

    if count is None:
        count = 20
    if count < 5:
        count = 20
    if count > 100:
        count = 100

    surges: Set[str] = set()
    attempts = 0
    while attempts < count * 2 and len(surges) < count:
        attempts += 1
        surges.add(rng.choice(SURGES).render(rng).capitalize())
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
