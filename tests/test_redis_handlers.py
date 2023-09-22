import logging
from unittest.mock import patch
import pytest

from base.redis_handlers import save_socket_user_mapping, get_socket_id_by_user_id, get_user_id_by_socket_id, \
    delete_socket_user_mapping
from utils.utils3 import connect_to_redis


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


@pytest.mark.asyncio
async def test_main_functions():
    socket = 11111111
    user = 22222222
    client = await connect_to_redis()
    response = await client.ping()
    assert response
    null_logger = logging.getLogger()
    null_logger.addHandler(NullHandler())
    with patch('logs.logs.my_logger', null_logger):
        await save_socket_user_mapping(socket_id=socket, user_id=user)

        socket_redis_id = await get_socket_id_by_user_id(user_id=user)
        user_redis_id = await  get_user_id_by_socket_id(socket_id=socket)
        assert int(socket_redis_id) == socket
        assert int(user_redis_id) == user
        await delete_socket_user_mapping(socket_id=socket_redis_id, user_id=user_redis_id)

        socket_redis_id = await get_socket_id_by_user_id(user_id=user)
        user_redis_id = await get_user_id_by_socket_id(socket_id=socket)
        assert not socket_redis_id
        assert not user_redis_id
