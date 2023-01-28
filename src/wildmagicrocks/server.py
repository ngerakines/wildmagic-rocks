import os
import logging
from typing import List, Optional, Set, Union
import jinja2
from aiohttp import web
import aiohttp_jinja2
import numpy as np
import spacy
import lemminflect

from wildmagicrocks.model import SurgeIndex, random_target


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

def seed_or(request) -> int:
    seed: Optional[int] = int_or(request.query.get("seed"), None)
    if seed is None:
        seed = np.random.randint(1, 9223372036854775807)
    return seed

async def handle_index(request):
    seed = seed_or(request)
    surges = request.config_dict["surge_index"].random_surges(seed)
    return aiohttp_jinja2.render_template("index.html", request, context={"surge": surges[0], "seed": seed})


async def handle_table(request):
    seed = seed_or(request)
    count = int_or(request.query.get("count"), 20)
    selected = int_or(request.query.get("selected"), 0)
    if selected == -1:
        select_rng = np.random.default_rng()
        selected = select_rng.integers(1, count)
        raise web.HTTPFound(f"/table?seed={seed}&count={count}&selected={selected}")
    surges = request.config_dict["surge_index"].random_surges(seed, count)
    if selected > len(surges):
        selected = 0

    return aiohttp_jinja2.render_template("table.html", request, context={"surges": surges, "seed": seed, "selected": selected, "count": count})


async def handle_surge(request):
    seed = seed_or(request)
    raw = str(request.query.get("raw")).lower().startswith("t")
    surge = request.config_dict["surge_index"].find_surge(seed, request.match_info["surge_id"], raw=raw)
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

    app["surge_index"] = SurgeIndex(surge_sources=[os.path.join(os.getcwd(), "surges.txt")])

    app.add_routes([web.static("/static", static_location(), append_version=True)])
    app.add_routes([web.get("/", handle_index)])
    app.add_routes([web.get("/table", handle_table)])
    app.add_routes([web.get("/surge/{surge_id}", handle_surge)])
    app.add_routes([web.get("/help", handle_help)])

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_location()))

    return app
