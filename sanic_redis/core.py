from sanic import Sanic
from aioredis import create_pool


class SanicRedis:
    def __init__(self, app: Sanic=None, redis_config: dict=None):
        self.app = app
        self.config = redis_config

        if app:
            self.init_app(app=app)

    def init_app(self, app: Sanic, redis_config: dict=None):
        self.app = app
        self.config = redis_config

        @app.listener('before_server_start')
        async def aio_redis_configure(_app, loop):
            _c = dict(loop=loop)
            if self.config:
                config = self.config
            else:
                config = _app.config.get('REDIS')
            for key in ['address', 'db', 'password', 'ssl', 'encoding', 'minsize',
                        'maxsize', 'create_connection_timeout']:
                if key in config:
                    _c.update({key: config.get(key)})
            _redis = await create_redis_pool(**_c)

            _app.redis = _redis

        @app.listener('after_server_stop')
        async def close_redis(_app, loop):
            _app.redis.close()
            await _app.redis.wait_closed()

    async def acquire(self):
        with await getattr(self.app, 'redis') as r:
            return r
