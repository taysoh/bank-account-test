import logging
import os

import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

from routes import setup_routes


async def get_courses(app):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.exchangeratesapi.io/latest?base=EUR') as response:
            if response.status == 200:
                rates = await response.json()
                rates = rates.get('rates')
            else:
                rates = {
                    'USD': 1.14,
                    'GBP': 0.89,
                    'JPY': 123.93,
                    'RUB': 77.06
                }
            app['rates'] = rates


async def init_app():
    app = web.Application()
    app['websockets'] = []
    app['rates'] = {}
    app.on_shutdown.append(shutdown)
    await get_courses(app)
    setup_routes(app)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.path.join(BASE_DIR, 'templates'))
    )
    return app


async def shutdown(app):
    for ws in app['websockets']:
        await ws.close()
    app['websockets'].clear()


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = init_app()

    web.run_app(app)


if __name__ == '__main__':
    main()
