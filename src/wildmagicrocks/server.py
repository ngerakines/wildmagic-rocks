import os
import logging
from typing import Any, Dict, Optional, Union
import jinja2
from aiohttp import web
import aiohttp_jinja2
import numpy

from wildmagicrocks.model import SurgeIndex, random_target
from wildmagicrocks.util import url_with_globals


logger = logging.getLogger(__name__)


def get_mode(request) -> Optional[str]:
    if "dark" in request.query:
        return "dark"
    elif "light" in request.query:
        return "light"
    return None


def get_seed(request) -> int:
    seed: Optional[int] = int_or(request.query.get("seed"), None)
    if seed is None:
        seed = numpy.random.randint(1, 9223372036854775807)
    return seed


def query_globals(request) -> Dict[str, Any]:
    result: Dict[str, Any] = {"globals": {}, "light_url": request.url.with_query({"light": "t"}), "dark_url": request.url.with_query({"dark": "t"})}
    mode = get_mode(request)
    if mode is not None:
        result["color_scheme"] = mode
        result["globals"][mode] = "t"
    return result


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
    seed = get_seed(request)
    global_query = query_globals(request)
    surges = request.config_dict["surge_index"].random_surges(seed)
    return await aiohttp_jinja2.render_template_async("index.html", request, context={"surge": surges[0], "seed": seed, **global_query})


async def handle_table(request):
    seed = get_seed(request)
    global_query = query_globals(request)
    count = int_or(request.query.get("count"), 20)
    selected = int_or(request.query.get("selected"), 0)
    if selected == -1:
        select_rng = numpy.random.default_rng()
        selected = select_rng.integers(1, count)
        raise web.HTTPFound(request.app.router.get("surge_table").url_for().with_query({"seed": str(seed), "count": count, "selected": str(selected), **global_query["globals"]}))
    surges = request.config_dict["surge_index"].random_surges(seed, count)
    if selected > len(surges):
        selected = 0
    return await aiohttp_jinja2.render_template_async("table.html", request, context={"surges": surges, "seed": seed, "selected": selected, "count": count, **global_query})


async def handle_surge(request):
    seed = get_seed(request)
    global_query = query_globals(request)

    raw = str(request.query.get("raw")).lower().startswith("t")
    surge = request.config_dict["surge_index"].find_surge(seed, request.match_info["surge_id"], raw=raw)
    if surge is None:
        raise web.HTTPNotFound()
    return await aiohttp_jinja2.render_template_async("surge.html", request, context={"surge": surge, "seed": seed, **global_query})


async def handle_help(request):
    global_query = query_globals(request)
    return await aiohttp_jinja2.render_template_async("help.html", request, context=global_query)


async def handle_rules(request):
    global_query = query_globals(request)
    return await aiohttp_jinja2.render_template_async("rules.html", request, context=global_query)


async def start_web_server():
    app = web.Application()

    app["surge_index"] = SurgeIndex(surge_sources=[os.path.join(os.getcwd(), "surges.txt")])

    app.add_routes([web.static("/static", os.path.join(os.getcwd(), "static"), append_version=True)])

    app.add_routes([web.get("/", handle_index, name="surge")])
    app.add_routes([web.get("/table", handle_table, name="surge_table")])
    app.add_routes([web.get("/surge/{surge_id}", handle_surge, name="surge_info")])
    app.add_routes([web.get("/help", handle_help, name="help")])
    app.add_routes([web.get("/rules", handle_rules, name="rules")])

    jinja_env = aiohttp_jinja2.setup(app, enable_async=True, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates")))
    jinja_env.globals.update(
        {
            "url": url_with_globals,
        }
    )

    app["static_root_url"] = "/static"

    return app
