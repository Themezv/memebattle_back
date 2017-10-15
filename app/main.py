from pathlib import Path

import aioredis
import asyncpg
from aiohttp import web, WSCloseCode

from .settings import Settings
from .views import index, websocket_handler
from .auth.views import create_user, check_auth_middleware

import aiohttp_cors

THIS_DIR = Path(__file__).parent
BASE_DIR = THIS_DIR.parent


def pg_dsn(settings: Settings) -> str:

    return '{drivername}://{username}:{password}@{host}:{port}/{database}'.format(
        database=settings.DB_NAME,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        username=settings.DB_USER,
        drivername='postgres')


async def startup(app: web.Application):
    app['pg'] = await asyncpg.create_pool(pg_dsn(app['settings']), loop=app.loop)
    app['redis'] = await aioredis.create_pool(('localhost', 6379), loop=app.loop, encoding='utf-8')


async def cleanup(app: web.Application):
    await app['pg'].close()
    app['redis'].close()
    await app['redis'].wait_closed()


def setup_routes(app, cors):
    app.router.add_get('/', index, name='index')
    app.router.add_route('*', '/ws', websocket_handler)
    app.router.add_put('/auth', create_user, name='create_user')
    cors.add(app.router['index'])


async def on_shutdown(app):
    for ws in app['websockets']:
        await ws.close(code=WSCloseCode.GOING_AWAY,
                       message='Server shutdown')


def create_app(loop):
    app = web.Application(middlewares=[check_auth_middleware])
    settings = Settings()
    app.update(
        name='memebattle_back',
        settings=settings
    )

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    app['websockets'] = []
    app['perms_handlers'] = []
    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)
    app.on_shutdown.append(on_shutdown)

    setup_routes(app, cors)
    return app
