from redis import Redis

from config import settings


REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT

# redis_cache = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

redis_url ='rediss://red-csvlm6d2ng1s73dtbc1g:PBAGFWxSzyKH2WBuqFoCeCfaiMsskUL8@oregon-redis.render.com:6379'

redis_cache = Redis.from_url(redis_url, decode_responses=True)