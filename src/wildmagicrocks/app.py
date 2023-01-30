import os
from aiohttp import web
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from wildmagicrocks.config import configure_logging
from wildmagicrocks.server import start_web_server


def main():
    configure_logging()
    web.run_app(start_web_server())


if __name__ == "__main__":
    if os.getenv("SENTRY_DSN"):
        sentry_sdk.init(integrations=[AioHttpIntegration()])
    main()
