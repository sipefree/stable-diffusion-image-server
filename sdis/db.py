from redis.asyncio import client, from_url
from sanic import DefaultSanic, Request
from sanic.log import logger




class RedisManager:
    
    def __init__(self, redis: client.Redis):
        self.conn = redis
        
    @classmethod
    async def connect_app(cls, app: DefaultSanic, redis_url: str):
        if not redis_url:
            raise ValueError("You must specify a redis_url for RedisManager.")
        logger.info('[RedisManager] connecting')
        conn = await from_url(redis_url)
        app.ctx.redis = cls(conn)
        
        @app.listener('after_server_stop')
        async def close_redis(app: DefaultSanic):
            logger.info('[RedisManager] closing')
            await app.ctx.redis.conn.close()
            
        # ------------------------------- Dependencies ------------------------------- #
        
        def get_conn(request: Request) -> client.Redis:
            return request.app.ctx.redis.conn
        
        app.ext.add_dependency(client.Redis, get_conn)
        
        # ---------------------------------------------------------------------------- #
        
        def get_redis(request: Request) -> RedisManager:
            return request.app.ctx.redis
        
        app.ext.add_dependency(RedisManager, get_redis)
        
        # ---------------------------------------------------------------------------- #
        

        
        
        
        
    
    