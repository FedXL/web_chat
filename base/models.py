from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, Text, func, CheckConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship

from handlers.pydentic_models import MessageDetails

Base = declarative_base()
BaseBot = declarative_base()


class WebUser(Base):
    __tablename__ = 'web_users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    is_kazakhstan = Column(Boolean)
    last_online = Column(TIMESTAMP)
    last_message_telegramm_id = Column(BigInteger)

    messages_relationship = relationship('WebMessage', back_populates='user_relationship')


class WebMessage(Base):
    __tablename__ = 'web_messages'
    id = Column(BigInteger, primary_key=True)
    message_body = Column(String)
    is_answer = Column(Boolean)
    user = Column(Integer, ForeignKey('web_users.user_id'), nullable=False)
    time = Column(TIMESTAMP, server_default=func.now())
    message_type = Column(String)
    user_relationship = relationship("WebUser", back_populates="messages_relationship")

    def as_dict(self):
        result = {'message_id': self.id,
                  'text': self.message_body,
                  'is_answer': self.is_answer,
                  'user_id': self.user,
                  'time': self.time.isoformat(),
                  'message_type': self.message_type,
                  }

        return result

    __table_args__ = (
        CheckConstraint(message_type.in_(['text', 'photo', 'file', 'caption']), name='check_message_type'),
    )

    def __repr__(self):
        return f"{self.id} | {self.message_body} | {self.is_answer} | {self.time}"


class Message(Base):
    __tablename__ = 'messages'
    id = Column(BigInteger, primary_key=True)
    message_body = Column(String)
    is_answer = Column(Boolean)
    storage_id = Column(BigInteger, ForeignKey('users.user_id'))
    time = Column(TIMESTAMP, default=func.now())
    message_id = Column(BigInteger)


class WebPhoto(Base):
    __tablename__ = 'web_photos'
    id = Column(Integer, primary_key=True)
    photo_path = Column(String)
    message_id = Column(Integer, ForeignKey('web_messages.id'))


class WebSocket(Base):
    __tablename__ = 'websockets'
    id = Column(BigInteger, primary_key=True)
    socket_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey('web_users.user_id'), unique=True)


class Jwt(Base):
    __tablename__ = 'jwt'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('web_users.user_id'), unique=True)
    jwt_hash = Column(String)


class Posts(BaseBot):
    """Таблица постов (cms sistem) в каналах"""
    __tablename__ = 'posts'
    id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger)
    chat_id = Column(BigInteger)
    name = Column(String, unique=True)

    def __repr__(self):
        return f"mess: {self.message_id} | chat: {self.chat_id} | name: {self.name}"


class OrderStatus(BaseBot):
    __tablename__ = 'order_status'
    id = Column(BigInteger, primary_key=True)
    status = Column(Boolean)
    order_id = Column(Integer, ForeignKey('orders.id'))
    manager_id = Column(BigInteger)
    order_price = Column(String, nullable=False)

    def __repr__(self):
        return f'{self.order_id} | {self.order_price} | {self.status}'


class Order(BaseBot):
    __tablename__ = 'orders'
    id: int = Column(Integer, primary_key=True)
    client: int = Column(BigInteger, nullable=False)
    buyer: int = Column(BigInteger)
    time = Column(TIMESTAMP, nullable=False)
    type: str = Column(String, nullable=False)
    body: str = Column(Text, nullable=False)

    def __repr__(self):
        return f'{self.id} | {self.client} | {self.time} | {self.type}'


class User(BaseBot):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    message_id = Column(Integer)
    user_second_name = Column(String)
    tele_username = Column(String)
    main_user = Column(String)
    is_kazakhstan = Column(Boolean)

    def __repr__(self):
        return f"{self.user_id} | {self.user_name} | {self.user_second_name} | {self.tele_username}"


class UserData(BaseBot):
    __tablename__ = 'users_app'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)


class Discount(BaseBot):
    __tablename__ = 'discounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_vip = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)


class Photo(BaseBot):
    __tablename__ = 'photos'
    photo_id = Column(Integer, primary_key=True)
    file_id = Column(Text)
    message_id = Column(Integer, ForeignKey('messages.id'))


class Document(BaseBot):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    document_id = Column(Text)
    message_id = Column(Integer, ForeignKey('messages.id'))


class Manager(BaseBot):
    __tablename__ = 'managers'
    id = Column(BigInteger, primary_key=True)
    short_name = Column(String, unique=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    key = Column(String, unique=True)
    is_active = Column(Boolean)

