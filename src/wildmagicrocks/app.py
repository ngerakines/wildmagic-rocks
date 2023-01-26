from aiohttp import web

from wildmagicrocks.config import configure_logging
from wildmagicrocks.server import start_web_server

def main():
    configure_logging()
    web.run_app(start_web_server())

if __name__ == "__main__":
    main()
