from redis import Redis

from config import settings


REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT

redis_cache = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)