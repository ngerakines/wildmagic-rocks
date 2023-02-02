import os
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
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


def get_surge_filters(request) -> Tuple[Optional[Set[str]], Optional[Set[str]]]:
    include_tags: Optional[Set[str]] = None
    exclude_tags: Optional[Set[str]] = None
    include: Optional[str] = request.query.get("include", None)
    if include is not None:
        include_values = []
        for include_value in include.split(","):
            include_value = include_value.strip().lower()
            if len(include_value) > 0:
                include_values.append(include_value)
        if len(include_values) > 0:
            include_tags = frozenset(include_values)
    exclude: Optional[str] = request.query.get("exclude", None)
    if exclude is not None:
        exclude_values = []
        for exclude_value in exclude.split(","):
            exclude_value = exclude_value.strip().lower()
            if len(exclude_value) > 0:
                exclude_values.append(exclude_value)
        if len(exclude_values) > 0:
            exclude_tags = frozenset(exclude_values)
    return include_tags, exclude_tags


def query_globals(request) -> Tuple[Dict[str, Any], Optional[Set[str]], Optional[Set[str]]]:
    include_tags, exclude_tags = get_surge_filters(request)
    result: Dict[str, Any] = {
        "globals": {},
        "light_url": request.url.with_query({"light": "t"}),
        "dark_url": request.url.with_query({"dark": "t"}),
        "filters": sorted(request.config_dict["surge_index"].all_filters()),
    }
    if include_tags is not None:
        result["globals"]["include"] = ",".join(list(sorted(include_tags)))
        result["include"] = ",".join(list(sorted(include_tags)))
    if exclude_tags is not None:
        result["globals"]["exclude"] = ",".join(list(sorted(exclude_tags)))
        result["exclude"] = ",".join(list(sorted(exclude_tags)))
    mode = get_mode(request)
    if mode is not None:
        result["color_scheme"] = mode
        result["globals"][mode] = "t"
    return result, include_tags, exclude_tags


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
    global_query, include_tags, exclude_tags = query_globals(request)
    surges = request.config_dict["surge_index"].random_surges(
        seed, count=1, include_tags=include_tags, exclude_tags=exclude_tags
    )
    if len(surges) == 0:
        return await aiohttp_jinja2.render_template_async(
            "error.html",
            request,
            context={"error_message": "No surges match that criteria.", "seed": seed, **global_query},
        )
    return await aiohttp_jinja2.render_template_async(
        "index.html", request, context={"surge": surges[0], "seed": seed, **global_query}
    )


async def handle_table(request):
    seed = get_seed(request)
    global_query, include_tags, exclude_tags = query_globals(request)
    count = int_or(request.query.get("count"), 20)
    selected = int_or(request.query.get("selected"), 0)
    if selected == -1:
        select_rng = numpy.random.default_rng()
        selected = select_rng.integers(1, count)
        raise web.HTTPFound(
            request.app.router.get("surge_table")
            .url_for()
            .with_query({"seed": str(seed), "count": count, "selected": str(selected), **global_query["globals"]})
        )
    surges = request.config_dict["surge_index"].random_surges(
        seed, count, include_tags=include_tags, exclude_tags=exclude_tags
    )
    if selected > len(surges):
        return await aiohttp_jinja2.render_template_async(
            "error.html", request, context={"error_message": "Invalid selected surge", "seed": seed, **global_query}
        )
    if len(surges) == 0:
        return await aiohttp_jinja2.render_template_async(
            "error.html",
            request,
            context={"error_message": "No surges match that criteria.", "seed": seed, **global_query},
        )
    return await aiohttp_jinja2.render_template_async(
        "table.html",
        request,
        context={"surges": surges, "seed": seed, "selected": selected, "count": count, **global_query},
    )


async def handle_surge(request):
    seed = get_seed(request)
    global_query, _, _ = query_globals(request)

    raw = str(request.query.get("raw")).lower().startswith("t")
    surge = request.config_dict["surge_index"].find_surge(seed, request.match_info["surge_id"], raw=raw)
    if surge is None:
        raise web.HTTPNotFound()
    return await aiohttp_jinja2.render_template_async(
        "surge.html", request, context={"surge": surge, "seed": seed, **global_query}
    )


async def handle_spell_surges(request):
    global_query, _, _ = query_globals(request)
    surges: List[Tuple[str, str, List[str]]] = sorted(request.config_dict["surge_index"].export(), key=lambda x: x[1])
    return await aiohttp_jinja2.render_template_async(
        "surges.html", request, context={"surges": surges, **global_query}
    )


async def handle_help(request):
    global_query, _, _ = query_globals(request)
    return await aiohttp_jinja2.render_template_async("help.html", request, context=global_query)


async def handle_rules(request):
    global_query, _, _ = query_globals(request)
    return await aiohttp_jinja2.render_template_async("rules.html", request, context=global_query)


async def start_web_server():
    app = web.Application()

    app["surge_index"] = SurgeIndex(surge_sources=[os.path.join(os.getcwd(), "surges.txt")])

    app.add_routes([web.static("/static", os.path.join(os.getcwd(), "static"), append_version=True)])

    app.add_routes([web.get("/", handle_index, name="surge")])
    app.add_routes([web.get("/table", handle_table, name="surge_table")])
    app.add_routes([web.get("/surge/{surge_id}", handle_surge, name="surge_info")])
    app.add_routes([web.get("/surges", handle_spell_surges, name="surges")])
    app.add_routes([web.get("/help", handle_help, name="help")])
    app.add_routes([web.get("/rules", handle_rules, name="rules")])

    jinja_env = aiohttp_jinja2.setup(
        app, enable_async=True, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
    )
    jinja_env.globals.update(
        {
            "url": url_with_globals,
        }
    )

    app["static_root_url"] = "/static"

    return app
