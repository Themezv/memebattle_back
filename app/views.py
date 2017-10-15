import aiohttp
import json

from aiohttp import web

from app.game.controllers import Game

async def index(request):
    await request.app['Game'].create_game()
    with await request.app['redis'] as redis:
        val = await redis.get('artem')
    return web.json_response({'val': val})


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
                        print('CHHOSE_MEM: {}'.format(data))
                        await game.add_choosed(ws)
                        left, right = await game.inc_like(data['id'])
                        for user_ws in await game.get_choosed():
                            user_ws.send_json({
                            'data': [json.loads(left), json.loads(right)],
                            'type': 'MEMES_LIKES'
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