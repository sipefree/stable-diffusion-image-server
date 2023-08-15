from redis.asyncio import client, from_url
from sanic import Sanic
from sanic.log import logger


class RedisManager:
    _instance = None
    
    def __new__(cls) -> 'RedisManager':
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls.instance.connection_Pool = None
        return cls._instance

    async def get_connection(self) -> redis.Redis:
        if not self.connection_pool:
            self.connection_pool = redis.ConnectionPool(
                host='localhost', port=6379, decode_responses=True, encoding='utf-8'
            )
        return redis.Redis(connection_pool=self.connection_pool)