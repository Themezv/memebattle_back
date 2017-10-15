import asyncpg
from aiohttp import web
import asyncio
import json

async def create_game(request):
    with await request.app['redis'] as redis:
        # pipe = redis.pipeline()
        try:
            left, right = await redis.hvals('current_pair')
            print(f'Left: {left}')
            print(f'Right: {right}')
        except ValueError:
            await redis.hmset_dict('current_pair', {'left': 'value1', 'right': 'value2'})
        # fut2 = pipe.hset('current_pair', 'left', )
        # pipe.set('Artem', 'Is cool')
        # result = await pipe.execute()
        await redis.se
    return web.json_response({'all': 'right'})


class Game:

    def __init__(self, redis, pg, shelduer, websockets):
        self.redis = redis
        self.pg = pg
        self._choosed = []
        self._stage = 1
        self.memes_ids = []
        self.current_pair_id = 1
        self.websockets = websockets
        self.shelduer = shelduer

    async def get_current_pair(self):
        print('Get current pair')
        with await self.redis as redis:
            return await redis.hmget('memes', *self.memes_ids[self.current_pair_id*2:self.current_pair_id*2+2])

    async def create_game(self):
        print('Create game')
        with await self.redis as redis:
            async with self.pg.acquire() as connect:
                for mem in await connect.fetch('SELECT * FROM bd3 WHERE likes > 5000 LIMIT 32;'):
                    await redis.hset('memes', mem['index'], json.dumps({
                            'url': mem['img'],
                            'id': mem['index'],
                            'likes': 0,
                        }))

            self.memes_ids = await redis.hkeys('memes')
            await self.go()
            print(self.memes_ids[1:3])

    async def go(self):
        await self.shelduer.spawn(self.next_timer())

    async def next_timer(self):
        print(f'CURRENT PAIR ID: {self.current_pair_id}')
        for user_ws in self.websockets:
            user_ws.send_json({
                'type': 'START_TIMER',
                'data': [json.loads(x) for x in await self.get_current_pair()]
            })
        await asyncio.sleep(5)
        await self.clear_choosed()
        le, ri = await self.get_current_pair()
        left = json.loads(le)
        right = json.loads(ri)
        if left['likes'] >= right['likes']:
            winner_id = left['id']
        else:
            winner_id = right['id']
        for user_ws in self.websockets:
            user_ws.send_json({
                'type': 'END_TIMER',
                'data': {
                    'winner_id': winner_id,
                    'coins': 10
                }
            })
        print(f'left: {left["id"]}. right: {right["id"]}')
        if self.current_pair_id < (len(self.memes_ids)-2)/2:
            self.current_pair_id+=1
        else:
            self.current_pair_id = 0
        print('next Timer')
        await asyncio.sleep(3.0)
        await self.shelduer.spawn(self.next_timer())

    async def add_choosed(self, ws):
        print('Add choosed')
        self._choosed.append(ws)
        print('Success add choosed')

    async def get_choosed(self):
        print('Get choosed')
        return self._choosed

    async def del_choosed(self, ws):
        if ws in self._choosed:
            self._choosed.remove(ws)

    async def clear_choosed(self):
        self._choosed = []

    async def inc_like(self, input_id):
        le, ri = await self.get_current_pair()
        left = json.loads(le)
        right = json.loads(ri)
        print(f'left: {left}. type: {type(left["likes"])}')

        with await self.redis as redis:
            if left['id'] == input_id:
                left['likes'] += 1
                await redis.hset('memes', left['id'], json.dumps(left))
            else:
                right['likes'] += 1
                await redis.hset('memes', right['id'], json.dumps(right))

        return left, right


    async def get_stage(self):
        return self._stage

