import aiohttp
import json

from aiohttp import web


async def index(request):
    with await request.app['redis'] as redis:
        val = await redis.get('artem')
    return web.json_response({'val': val})


async def websocket_handler(request):
    ws = web.WebSocketResponse()
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
                        print('choose {} mem'.format(data['id']))
                        ws.send_json({
                            'data': [{'memes': 1, 'likes': 10}, {'memes': 2, 'likes': 15}],
                            'type': 'MEMES_LIKES'
                        })
                    # for soc in request.app['websockets']:
                    #     await soc.send_json(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())
    finally:
        print('Final')
        request.app['websockets'].remove(ws)

    print('websocket connection closed')

    return ws