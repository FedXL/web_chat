import hashlib
from sqlalchemy import select, desc, delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
from sqlalchemy.orm import selectinload
from base.engines import async_engine
from base.models import WebUser, Jwt, WebSocket, WebMessage, WebPhoto, Message, Photo
from config.config_bot import async_engine_bot, SUPER_WEB_USER
from handlers.pydentic_models import MessageType, HistoryDetails
from logs.logs import my_logger


async def add_photo_to_db_bot(
        photo_id: str,
        is_answer: bool,
        user_id: int = SUPER_WEB_USER,
        message_id: int = None):

    my_logger.debug('start')
    prefix = '/photo_'
    try:
        async with AsyncSession(async_engine_bot) as session:
            async with session.begin():
                if message_id:
                    new_message = Message(is_answer=is_answer, storage_id=user_id, message_id=message_id)
                else:
                    new_message = Message(is_answer=is_answer, storage_id=user_id)

                session.add(new_message)
                await session.flush()
                message_id_in_db: int = new_message.id
                session.add(Photo(file_id=photo_id, message_id=message_id_in_db))
                photo_command = prefix + str(message_id_in_db)
                await session.execute(
                    update(Message).where(Message.id == message_id_in_db).values(message_body=photo_command))
                await session.commit()
                my_logger.debug(f'finish {photo_command}')
                return photo_command

    except Exception as Error:
        my_logger.debug(f'all is bad {Error}')


async def update_text_in_message_in_web_db(web_message_id: int, text: str):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = update(WebMessage).where(WebMessage.id == web_message_id).values(message_body=text)
            await session.execute(stmt)
            await session.commit()


async def save_photo_message_to_web_db(
        is_answer: bool,
        user_id: int,
        message_type: str,
        text: str,
        message_id: int | None = None,
        extension: str = None,
        time=None,
        bot_command=None,
):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            new_message = WebMessage(message_body=bot_command,
                                     is_answer=is_answer,
                                     user=user_id,
                                     message_type=message_type)
            session.add(new_message)
            await session.flush()
            message_id = new_message.id
            photo = WebPhoto(photo_path=text,
                             message_id=message_id)
            session.add(photo)
            await session.flush()
            return message_id


async def create_user(name):
    my_logger.debug(f'start foo with name: {name}')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            created_time = datetime.datetime.now()
            user = WebUser(user_name=name,
                           is_kazakhstan=True,
                           last_online=created_time)
            session.add(user)
            await session.flush()
            user_id = user.user_id
            await session.commit()
    return user_id


async def associate_user_with_token(user_id, token):
    my_logger.debug('start')
    token_hash = hashlib.sha256(token.split('.')[2].encode()).hexdigest()
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            jwt_token = Jwt(user_id=user_id,
                            jwt_hash=token_hash)
            session.add(jwt_token)
            await session.flush()
            if jwt_token.id:
                my_logger.debug(f'success token_id: {jwt_token.id}')
                await session.commit()
            else:
                my_logger.error(f'fail')


async def get_user_by_token(token: str) -> int:
    my_logger.debug('start')
    token_hash = hashlib.sha256(token.split('.')[2].encode()).hexdigest()
    try:
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                stmt = select(Jwt.user_id).where(Jwt.jwt_hash == token_hash)
                result = await session.execute(stmt)
                user_id = result.scalar()
                return user_id
    except Exception as ER:
        my_logger.error(f'Cannot to get user by token {ER}')


async def associate_user_with_socket(user_id, socket_id):
    my_logger.debug(f'start with user {user_id} socket {socket_id}')
    try:
        socket_id = int(socket_id)
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                websocket = WebSocket(socket_id=socket_id, user_id=user_id)
                session.add(websocket)
                await session.commit()
    except Exception as ER:
        my_logger.error(f'database er {ER}')


async def download_history(user_id: int, is_for_meeting_message=False) -> list[HistoryDetails]:
    """Честно пытался разобраться с relationships но нифига не понял. Как у двух моделей
    строить понятно, а как у трех моделей связяанных внешними ключами photo-fk->message-fk->user
    как построить relationship отношение photo<-message->user не понимаю хоть убей"""

    async with AsyncSession(async_engine) as session:
        async with session.begin():
            if is_for_meeting_message:
                stmt = select(WebMessage).where(WebMessage.user == user_id).order_by(desc(WebMessage.time)).options(
                    selectinload(WebMessage.user_relationship))
            else:
                stmt = select(WebMessage).where(WebMessage.user == user_id).order_by((WebMessage.time)).options(
                    selectinload(WebMessage.user_relationship))
            messages = await session.execute(stmt)
            messages = messages.scalars()
            history = []
            for mess in messages:
                mess_dict = mess.as_dict()
                mess_dict['user_name'] = mess.user_relationship.user_name
                hist = HistoryDetails(**mess_dict)

                if hist.is_answer:
                    manager_name = hist.text.split(':', 1)[0]
                    hist.user_name = manager_name

                if not is_for_meeting_message:
                    if hist.message_type == 'photo':
                        stmt = select(WebPhoto.photo_path).where(WebPhoto.message_id == hist.message_id)
                        photo = await session.execute(stmt)
                        photo_path = photo.scalar()
                        hist.text = photo_path

                history.append(hist)
    return history


async def get_name_from_db(user_id: int):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(WebUser.user_name).where(WebUser.user_id == user_id)
            result = await session.execute(stmt)
            username = result.scalar()
            return username


async def save_message_to_db(message_id: int | None,
                             is_answer: bool,
                             user_id: int | None,
                             message_type: MessageType,
                             text: str | None,
                             token=None,
                             extension=None,
                             time=None):
    """is_answer = false -> from user / is_answer = true -> from manager"""
    my_logger.debug('try to save message')
    assert token or user_id, 'you should indicate user by id or token. token and user_id cant be None together'
    assert not (token and user_id), 'Choose smth one, user_id or token'

    try:
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                if token:
                    token_hash = hashlib.sha256(token.split('.')[2].encode()).hexdigest()
                    stmt = select(Jwt.user_id).where(Jwt.jwt_hash == token_hash)
                    result = await session.execute(stmt)
                    user_id: str = result.scalar()
                new_message = WebMessage(message_body=text, message_type=message_type,
                                         is_answer=is_answer, user=user_id)
                session.add(new_message)
                await session.flush()
                id = new_message.id
                await session.commit()
                my_logger.debug('message was successfully saved')
                return id

    except Exception as ER:
        my_logger.error(f'Cannot to save message {text} error: {ER}')
        raise ArithmeticError


async def remove_socket_from_db(socket_id: int):
    my_logger.debug(f'start to kill socket: {socket_id} ')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = delete(WebSocket).where(WebSocket.socket_id == socket_id)
            await session.execute(stmt)
            await session.commit()
    my_logger.debug(f'{socket_id} socket was successfully killed')


async def refresh_old_token(old_token, new_token):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            token_hash_old = hashlib.sha256(old_token.split('.')[2].encode()).hexdigest()
            stmt = select(Jwt.user_id).where(Jwt.jwt_hash == token_hash_old)
            user = await session.execute(stmt)
            user_id = user.scalar()
            if user_id:
                stmt_delete = delete(Jwt).where(Jwt.jwt_hash == token_hash_old)
                await session.execute(stmt_delete)
                token_hash_new = hashlib.sha256(new_token.split('.')[2].encode()).hexdigest()
                jwt_token = Jwt(user_id=user_id, jwt_hash=token_hash_new)
                session.add(jwt_token)
                await session.commit()
                return True
            else:
                return False


async def is_kazakhstan_chat(user_id: int):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(WebUser.is_kazakhstan).where(WebUser.user_id == user_id)
            result = await session.execute(stmt)
            is_kz = result.scalar()
            return is_kz


async def save_message_id_to_user(message_id: int, user_id: int):
    # message_id from telegram message
    my_logger.debug('start')
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = update(WebUser).where(WebUser.user_id == user_id).values(last_message_telegramm_id=message_id)
            await session.execute(stmt)
            await session.commit()
            my_logger.debug('finish')


async def get_message_id(user_id: int):
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            stmt = select(WebUser.last_message_telegramm_id).where(WebUser.user_id == user_id)
            result = await session.execute(stmt)
            user_id = result.scalar()
            return user_id
