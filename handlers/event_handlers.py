import base64

import os

from base.db_handlers import save_message_to_db, get_name_from_db, add_photo_to_db_bot, save_photo_message_to_web_db, \
    update_text_in_message_in_web_db
from base.redis_handlers import send_message_to_bot
from bot.bot_handlers import get_telegram_photo_id, send_meeting_message_to_bot
from config.config_app import STATIC_PATH
from handlers.pydentic_models import MessageLoad, Event, MessageDetails
from logs.logs import my_logger
from utils.utils3 import generate_random_filename


async def save_image_to_server(message_id: int | None,
                               is_answer: bool,
                               user_id: int | None,
                               message_type: str,
                               text: str,
                               extension: str,
                               time=None):
    # text, user_id, message_type, extension,):
    my_logger.debug(f"start{user_id}")
    if message_type == 'message':
        my_logger.debug(f"end because it is a text message")
        return
    elif message_type == 'photo':
        my_logger.debug('it is a photo')
    elif message_type == 'document':
        my_logger.debug('it is a pdf document')
    else:
        my_logger.error(f'wrong message type {message_type}')
        return

    new_name = generate_random_filename(extension=extension)
    directory = STATIC_PATH + "/" + "/images" + "/" + str(user_id) + "/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name = directory + new_name
    binary_data = base64.b64decode(text)

    with open(file_name, 'wb') as f:
        f.write(binary_data)
    url = f"/static/images/{user_id}/{new_name}"
    return url


async def message_event_handler(data: MessageLoad, ws):
    """обрабатывает все message events от клиента"""
    my_logger.debug(f"start")
    data.name = await get_name_from_db(user_id=data.details.user_id)
    if data.details.message_type in ('photo', 'document'):
        my_logger.debug('start photo or document branch')
        filename = await save_image_to_server(**data.details.model_dump())
        data.details.text = filename
        await ws.send_str(data.model_dump_json())
        web_message_id = await save_photo_message_to_web_db(**data.details.model_dump())
        telegram_document_id = await get_telegram_photo_id(filename)
        photo_command = await add_photo_to_db_bot(photo_id=telegram_document_id,
                                                  is_answer=data.details.is_answer,
                                                  message_id=web_message_id)
        await update_text_in_message_in_web_db(web_message_id, text=photo_command)
        await send_meeting_message_to_bot(user_id=data.details.user_id,
                                          user_name=data.name,
                                          full_history=False)

    elif data.details.message_type in ('text'):
        my_logger.debug('start text brunch')
        message_id = await save_message_to_db(**data.details.model_dump())
        data.details.message_id = message_id
        await ws.send_str(data.model_dump_json())
        await send_meeting_message_to_bot(user_id=data.details.user_id,
                                          user_name=data.name,
                                          full_history=False)
    else:
        my_logger.error(f"Undefinded message type: {data.details.message_type}, should be photo,document or text")
        return


