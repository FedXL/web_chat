import datetime
import hashlib
from base.db_handlers import create_user, associate_user_with_token, associate_user_with_socket, download_history
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from base.models import WebUser, WebSocket, Jwt
from base.engines import async_test_engine


@pytest.mark.asyncio
async def test_1(mocker, token, create_bd):
    mocker.patch('base.db_handlers.async_engine', async_test_engine)
    user_id = await create_user("Zebra 123")
    assert user_id == 1
    user_id = await create_user("Zebra 2")
    assert user_id == 2


@pytest.mark.asyncio
async def test_2(mocker, token, create_bd):
    mocker.patch('base.db_handlers.async_engine', async_test_engine)
    user_id = await create_user("Zebra 1223")
    assert user_id == 1
    user_id = await create_user("Zebra 22")
    assert user_id == 2


@pytest.mark.asyncio
async def test_create_user(mocker, token, create_bd):
    mocker.patch('base.db_handlers.async_engine', async_test_engine)
    user_id = await create_user("Zebra")
    socket_id = 66631231

    assert user_id == 1
    user_id: int = await create_user('Fed')
    assert user_id == 2

    await associate_user_with_token(user_id, token=token)
    await associate_user_with_socket(user_id=user_id,
                                     socket_id=socket_id)

    async with AsyncSession(async_test_engine) as session:
        async with session.begin():
            stmt = select(WebUser).where(WebUser.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            assert user.user_name == "Fed"
            assert user.is_kazakhstan == True
            assert isinstance(user.last_online, datetime.datetime)

            stmt = select(WebSocket).where(WebSocket.user_id == user_id)
            result = await session.execute(stmt)
            socket = result.scalar_one_or_none()
            assert socket.socket_id == socket_id

            stmt = select(Jwt).where(Jwt.user_id == user_id)
            result = await session.execute(stmt)
            jwt = result.scalar_one_or_none()

            assert jwt.jwt_hash == hashlib.sha256(token.split('.')[2].encode()).hexdigest()


@pytest.mark.skip
@pytest.mark.asyncio
async def test_download_history(mocker, token, create_bd, create_message_example):
    mocker.patch('base.db_handlers.async_engine', async_test_engine)
    messages = await download_history(user_id='1')
    assert len(messages) == 10
    for mes in messages:
        assert isinstance(mes.get('is_answer'), bool)
        assert mes.get('time')
        assert mes.get('body')

    timer = messages[0].get('time')
    messages.pop(0)
    for mes in messages:
        assert mes.get('time') < timer
        timer = mes.get('time')
