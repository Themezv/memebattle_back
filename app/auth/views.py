import asyncpg
from aiohttp import web
from hashlib import sha256


async def check_user(request) -> bool:
    data = await request.json()
    print('check user')
    print(str(data))
    print(sha256(str.encode(str(request.app['settings'].SECRET_PASSWORD) + data['password'])).hexdigest())

    async with request.app['pg'].acquire() as connect:
        user = await connect.fetchrow('SELECT * FROM users WHERE username = $1', data['username'])
        print('this is user')
        print(user['password'])
        hashed_pass = sha256(str.encode(str(request.app['settings'].SECRET_PASSWORD) + data['password']))
        return user['password'] == hashed_pass.hexdigest()


async def check_auth_middleware(app, handler):
    async def middleware_handler(request):
        if handler not in app['perms_handlers']:
            return await handler(request)
        if await check_user(request):
            return await handler(request)
        else:
            raise web.HTTPForbidden()
    return middleware_handler


async def create_user(request):
    data = await request.json()
    if not data['password'] and not data['username']:
        raise web.HTTPBadRequest()
    password_hash = sha256(str.encode((request.app['settings'].SECRET_PASSWORD) + data['password']))
    async with request.app['pg'].acquire() as connect:
        try:
            await connect.execute("INSERT INTO users(username, password) VALUES($1, $2)",
                              data['username'], password_hash.hexdigest())
        except asyncpg.exceptions.UniqueViolationError:
            return web.json_response({'status': '400', 'message': 'user already exist'})
    return web.json_response({'status': '200'})
