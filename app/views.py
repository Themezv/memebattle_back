import aiohttp
import json

from aiohttp import web

from app.game.controllers import Game


async def index(request):
    #await request.app['Game'].create_game()
    # with await request.app['redis'] as redis:
    #     val = await redis.get('artem')
    return web.json_response({'stage': 0})


async def start_game(request):
    status = False
    if not request.app['game_started']:
        await request.app['Game'].create_game()
        status = 'created'
        request.app['game_started'] = True
    else:
        status = 'exist'

    return web.json_response({'game': status})


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    game = request.app['Game']
    await ws.prepare(request)
    request.app['websockets'].append(ws)
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    print('msg: {}'.format(msg.data))
                    data = json.loads(msg.data)
                    if data['type'] == 'CHOOSE_MEM':
                        print('CHOOSE_MEM: {}'.format(data))
                        if ws in await game.get_choosed():
                            ws.send_json('ТЫ УЖЕ ГОЛОСОВАЛ')
                        else:
                            await game.add_choosed(ws)
                            left, right = await game.inc_like(data['id'])
                            for user_ws in await game.get_choosed():
                                user_ws.send_json({
                                    'data': [left, right],
                                    'type': 'MEMES_LIKES'
                                })
                    elif data['type'] == 'GET_STAGE':
                        print('GET_STAGE')
                        ws.send_json({'type': 'STAGE', 'data': {'stage': await game.get_stage()}})
                    elif data['type'] == 'START_TIMER':
                        print('START_TIMER')
                        for user_ws in request.app['websockets']:
                            user_ws.send_json({
                                'type': 'START_TIMER',
                                'data': await game.get_clear_pair()
                            })
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())
    finally:
        print('Final')
        request.app['websockets'].remove(ws)
        await game.del_choosed(ws)

    print('websocket connection closed')

    return ws