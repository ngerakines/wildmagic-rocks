import os
import logging
import random
from typing import Optional, Set
import jinja2
from aiohttp import web
import aiohttp_jinja2

from wildmagicrocks.model import SURGES


logger = logging.getLogger(__name__)


async def handle_index(request):
    surge = random.choice(SURGES)
    the_surge = surge.render()
    return aiohttp_jinja2.render_template("index.html", request, context={"surge": the_surge})

async def handle_table(request):
    count: Optional[int] = int(request.query.get("count"))
    if count is None or count < 5:
        count = 20
    if count > 100:
        count = 100

    surges: Set[str] = set()
    attempts = 0
    while attempts < count * 2 and len(surges) < count:
        attempts += 1
        surges.add(
            random.choice(SURGES).render().capitalize()
        )
    return aiohttp_jinja2.render_template("table.html", request, context={"surges": surges})

def template_location() -> str:
    return os.path.join(os.getcwd(), "templates")

def static_location() -> str:
    return os.path.join(os.getcwd(), "static")

async def start_web_server():
    app = web.Application()

    app.add_routes(
        [web.static("/static", static_location(), append_version=True)]
    )
    app.add_routes([web.get("/", handle_index)])
    app.add_routes([web.get("/table", handle_table)])

    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(template_location())
    )

    return app
