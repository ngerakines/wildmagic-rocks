import os
import logging
from typing import Optional, Set, Union
import jinja2
from aiohttp import web
import aiohttp_jinja2
import numpy as np

from wildmagicrocks.model import find_surge, random_surges


logger = logging.getLogger(__name__)


def int_or(value: Optional[Union[str, int]], default_value: Optional[int]) -> Optional[int]:
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
    seed: Optional[int] = int_or(request.query.get("seed"), None)
    if seed is None:
        seed = np.random.randint(1, 9223372036854775807)
    rng = np.random.default_rng(seed)

    print(rng.bit_generator.state)
    surges = random_surges(rng)
    return aiohttp_jinja2.render_template("index.html", request, context={"surge": surges[0], "seed": seed})


async def handle_table(request):
    seed: Optional[int] = int_or(request.query.get("seed"), None)
    if seed is None:
        seed = np.random.randint(1, 9223372036854775807)
    rng = np.random.default_rng(seed)
    count = int_or(request.query.get("count"), 20)
    selected = int_or(request.query.get("selected"), 0)

    print(f"selected {selected}")
    if selected == -1:
        select_rng = np.random.default_rng()
        selected = select_rng.integers(1, count)
        raise web.HTTPFound(f"/table?seed={seed}&count={count}&selected={selected}")

    surges = random_surges(rng, count)
    if selected > len(surges):
        selected = 0

    return aiohttp_jinja2.render_template("table.html", request, context={"surges": surges, "seed": seed, "selected": selected, "count": count})


async def handle_surge(request):
    seed: Optional[int] = int_or(request.query.get("seed"), None)
    if seed is None:
        seed = np.random.randint(1, 9223372036854775807)
    rng = np.random.default_rng(seed)

    surge = find_surge(rng, request.match_info["surge_id"])
    if surge is None:
        raise web.HTTPNotFound()
    return aiohttp_jinja2.render_template("surge.html", request, context={"surge": surge, "seed": seed})


async def handle_help(request):
    return aiohttp_jinja2.render_template("help.html", request, context={})


def template_location() -> str:
    return os.path.join(os.getcwd(), "templates")


def static_location() -> str:
    return os.path.join(os.getcwd(), "static")


async def start_web_server():
    app = web.Application()

    app.add_routes([web.static("/static", static_location(), append_version=True)])
    app.add_routes([web.get("/", handle_index)])
    app.add_routes([web.get("/table", handle_table)])
    app.add_routes([web.get("/surge/{surge_id}", handle_surge)])
    app.add_routes([web.get("/help", handle_help)])

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_location()))

    return app
