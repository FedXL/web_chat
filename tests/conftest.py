import asyncio
import datetime
import hashlib
import sys
from unittest.mock import MagicMock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session

from config.config_app import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_TEST, DB_NAME
from utils.token import create_token
from base.models import Base, WebUser, WebSocket, Jwt, WebMessage

test_engine = create_async_engine(DB_TEST, echo=False)
Base.metadata.bind = test_engine
async_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

@pytest.fixture()
def create_bd():
    url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test"
    engine = create_engine(url, echo=False)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture()
def create_message_example(token):
    url = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}_test"
    engine = create_engine(url, echo=False)
    last_online = datetime.datetime.now() - datetime.timedelta(days=1)
    with Session(engine) as session:
        user = WebUser(user_name = 'TestUser',
                       is_kazakhstan = True,
                       last_online = last_online)
        session.add(user)
        session.flush()
        user_id = user.user_id
        user_socket = WebSocket(socket_id = '999999999',
                                user_id = user_id)
        token_hash = hashlib.sha256(token.split('.')[2].encode()).hexdigest()

        user_token = Jwt(user_id=user.user_id, jwt_hash=token_hash)
        session.add(user_socket)
        session.add(user_token)

        user_id = 1

        dialogue = [
            ("Вестерн Бот", "Слышал, у нас новый шериф в городе."),
            ("Ковбой123", "Да, это правда. Он приехал на дилижансе вчера."),
            ("Вестерн Бот", "Мне кажется, он не так уж и опытен."),
            ("Ковбой123", "Ну, время покажет, сможет ли он взять в руки пистолет."),
            ("Вестерн Бот", "Надеюсь, он быстрее наушника."),
            ("Ковбой123", "Ага, а то в этом городе сейчас неспокойно."),
            ("Вестерн Бот", "Золотые рудники манят разбойников."),
            ("Ковбой123", "Будем надеяться, что шериф справится с бандитами."),
            ("Вестерн Бот", "Придется ему взять в руки не только пистолет, но и лассо."),
            ("Ковбой123", "Точно, ведь в этом городе делаются ставки высокие."),
        ]


        base_time = datetime.datetime.now()
        for i, (sender, message_text) in enumerate(dialogue):
            is_answer = True if i % 2 == 0 else False
            current_time = base_time + datetime.timedelta(minutes=i)
            message = WebMessage(message_body=message_text, is_answer=is_answer, user=user_id, time=current_time)
            session.add(message)
        session.commit()





@pytest.fixture(scope="session")
def token():
    name = "Fedor"
    ip = '127.0.0.1'
    token = create_token(ip, name)
    yield token

@pytest.fixture(scope='function')
def mock_datetime_now_plus_2days(monkeypatch):
    FAKE_TIME = datetime.datetime.now() + datetime.timedelta(days=2)
    datetime_mock = MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = FAKE_TIME
    monkeypatch.setattr(datetime, "datetime", datetime_mock)

@pytest.fixture(scope='function')
def mock_datetime_now_plus_8days(monkeypatch):
    FAKE_TIME = datetime.datetime.now() + datetime.timedelta(days=8)
    datetime_mock = MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = FAKE_TIME
    monkeypatch.setattr(datetime, "datetime", datetime_mock)





