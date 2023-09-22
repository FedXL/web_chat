from base.redis_handlers import save_socket_user_mapping, get_socket_id_by_user_id, get_user_id_by_socket_id, \
    delete_socket_user_mapping
from utils.utils3 import connect_to_redis


async def main():
    socket = 11111111
    user = 22222222
    try:
        client = await connect_to_redis()
        response = await client.ping()
        if response:
            print("Подключение к Redis установлено.")
        else:
            print("Не удалось установить подключение к Redis.")
    except Exception as e:
        print("Ошибка при подключении к Redis:", e)
    try:
        await save_socket_user_mapping(socket_id=socket, user_id=user)
    except Exception as e:
        print('Oшибка в сохранении в редис', e)

    try:
        socket_redis_id = await get_socket_id_by_user_id(user_id=user)
        user_redis_id = await  get_user_id_by_socket_id(socket_id=socket)
        print(socket_redis_id)
        print(user_redis_id)

    except Exception as e:
        print('херня случается', e)

    try:
        await delete_socket_user_mapping(socket_id=socket_redis_id, user_id=user_redis_id)
    except Exception as e:
        print('удалить не получается', e)

    try:
        socket_redis_id = await get_socket_id_by_user_id(user_id=user)
        user_redis_id = await get_user_id_by_socket_id(socket_id=socket)
        print(socket_redis_id)
        print(user_redis_id)
        assert not socket_redis_id
        assert not user_redis_id
    except Exception as e:
        print('херня случается', e)

if __name__ == '__main__':
    main()