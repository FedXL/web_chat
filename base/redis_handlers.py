import redis
from typing_extensions import Dict

from logs.logs import my_logger
from utils.utils3 import connect_to_redis


async def save_socket_user_mapping(socket_id, user_id):
    redis_client = await connect_to_redis()
    await redis_client.set(f'socket:{socket_id}', user_id)
    await redis_client.set(f'user:{user_id}', socket_id)
    await redis_client.close()


async def get_user_id_by_socket_id(socket_id) -> int | None:
    my_logger.debug('start')
    redis_client = await connect_to_redis()
    user_id = await redis_client.get(f'socket:{socket_id}')
    await redis_client.close()
    try:
        user = (user_id.decode('utf-8'))
        print(user, type(user))
        user = int(user)
    except Exception as ER:
        user = user_id
        my_logger.error(f'user id from redis is None {ER}')
    my_logger.debug(f'finish with user: {user}')
    return user


async def get_socket_id_by_user_id(user_id):
    redis_client = await connect_to_redis()
    socket_id = await redis_client.get(f'user:{user_id}')
    await redis_client.close()
    try:
        socket = int(socket_id.decode('utf-8'))
    except Exception as ER:
        my_logger.error(f'socket id from redis is None {ER}')
        socket = socket_id
    print("[GET FROM REDIS]", socket)
    return socket


async def delete_socket_user_mapping(socket_id, user_id):
    redis_client = await connect_to_redis()
    try:
        await redis_client.delete(f'socket:{socket_id}', user_id)
    except Exception as ER:
        my_logger.error(f"Cant to delete socket from redis {ER}")
    try:
        await redis_client.delete(f'user:{user_id}', socket_id)
    except Exception as ER:
        my_logger.error(f"Cant to delete user from redis {ER}")
    await redis_client.close()


async def send_message_to_bot(user_id, text):
    channel = "message_to_server"
    redis_client = await connect_to_redis()
    redis_client.pubsub()
    data = {"event": "message",
            "type": 'text',
            'user_id': user_id,
            'text': text}
    data = str(data)
    await redis_client.publish(channel, data)
