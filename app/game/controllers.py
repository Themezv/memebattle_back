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
        print(await redis.get('Artem'))
    return web.json_response({'all': 'right'})


class Game:
    def __init__(self, redis):
        self.redis = redis
        self._choosed = []

    def get_clear_pair(self) -> dict:
        return {
            'left': json.dumps({
                'id': 1,
                'src': 'http://qqwf.ru',
                'likes': 0
            }),
            'right': json.dumps({
                'id': 2,
                'src': 'http://qqwf.ru',
                'likes': 0
            })}

    async def get_current_pair(self):
        print('Get current pair')
        with await self.redis as redis:
            try:
                left, right = await redis.hvals('current_pair')
            except ValueError:
                print('Value error in get current')
                await redis.hmset_dict('current_pair', self.get_clear_pair())
                left, right = await redis.hvals('current_pair')
            print(f'End get_current_pair: left: {left}====Right: {right}')
            return left, right

    async def create_game(self):
        print('Create game')
        with await self.redis as redis:
            await redis.hmset_dict('current_pair', self.get_clear_pair())

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

    async def inc_like(self, input_id):
        left, right = await self.get_current_pair()
        print('left:')
        left_as_dict = json.loads(left)
        right_as_dict = json.loads(right)
        if left_as_dict['id'] == input_id:
            left_as_dict['likes'] += 1
        else:
            left_as_dict['likes'] += 1
        with await self.redis as redis:
            await redis.hmset_dict('current_pair', {
                'left': json.dumps(left_as_dict),
                'right': json.dumps(right_as_dict)
            })
        return left, right