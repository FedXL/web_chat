import aioredis
import redis
import sys

from aioredis import Redis
from aioredis.client import PubSub
from config.config_app import REDIS_URL, TEST_MODE_A
import uuid

from config.config_bot import TEST_MODE


def generate_random_filename(extension=""):
    random_filename = str(uuid.uuid4())
    if extension:
        random_filename += f"{extension}"
    random_filename = random_filename.replace("-", "")
    return random_filename


def check_redis_connection():
    port = 6379
    host = 'localhost'
    client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    try:
        response = client.ping()
        if response:
            print("Redis is working.")
            return
    except Exception:
        raise ConnectionError(f"Couldn't connect to Redis. Host: {host}, Port: {port}")
    finally:
        client.close()


def check_sistem():
    print(sys.version)
    if sys.version_info >= (3, 11):
        print(Warning('[WARNING]On moment 15.08.2023 aioredis have problem with python 3.11. use 3.7 or 3.10 version'))
    if TEST_MODE_A:
        print("[INFO] start app in TEST MODE")
    else:
        print("[INFO] start app in SERVER MODE")

    if TEST_MODE:
        print('[INFO] start bot settings in TEST MODE')
    else:
        print("[INFO] start bot settings in SERVER MODE")


async def connect_to_redis_pubsub() -> PubSub:
    redis: Redis = await aioredis.from_url(REDIS_URL)
    pubsub: PubSub = redis.pubsub()
    await pubsub.subscribe("news")
    return pubsub


async def connect_to_redis() -> Redis:
    redis: Redis = await aioredis.from_url(REDIS_URL)
    return redis


async def get_ip(request):
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    else:
        ip = request.remote
    print(f"[INFO] request IP adress is {ip}")
    return ip
