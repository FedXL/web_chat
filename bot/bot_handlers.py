import asyncio
import json
import os

import aiogram.utils.markdown as md
from aiogram.types import Message,ParseMode
from base.db_handlers import is_kazakhstan_chat, save_message_id_to_user, download_history, get_message_id, \
    get_name_from_db
from bot.menu import get_keyboard_message_start
from bot.texts import make_mask_to_web_messages, make_message_text
from config.config_app import BASE_DIRECTORY
from config.config_bot import kazakhstan_chat, tradeinn_chat, alerts
from config.create_bot import bot
from logs.logs import my_logger


async def check_user_chat(user_id: int) -> int:
    result = await is_kazakhstan_chat(user_id)
    if result:
        chat = kazakhstan_chat
    else:
        chat = tradeinn_chat
    return chat


async def get_telegram_photo_id(file_path):
    my_logger.debug(f'start filepath {file_path}')
    base_directory = BASE_DIRECTORY
    file_path_f = base_directory + file_path
    # file_abs_paty = os.path.abspath(os.path.join(base_directory,file_path))
    my_logger.debug(f'try to send file {file_path_f}')
    response = await bot.send_photo(chat_id=alerts, photo=open(file_path_f, 'rb'))
    await asyncio.sleep(2)
    photo_id = response.photo[-1].file_id
    await bot.delete_message(response.chat.id, response.message_id)
    return photo_id


async def send_meeting_message_to_bot(user_id, user_name, full_history=False):
    my_logger.debug(f'start full_history {full_history}')

    history = await download_history(user_id=user_id, is_for_meeting_message=True)
    if not full_history:
        history = history[:5]
        history_prep = [(mes.is_answer, mes.text,) for mes in history]
        mask = await make_mask_to_web_messages(user_id=user_id, user_name=user_name)
        text = make_message_text(history_prep)
        text_to_send = md.text(mask, *text, sep='\n')
        print(text_to_send)
        chat = await check_user_chat(user_id=user_id)
    else:
        return

    try:
        old_message_id = await get_message_id(user_id)
        if old_message_id:
            try:
                await bot.delete_message(chat, old_message_id)
            except:
                print('not')
        message: Message = await bot.send_message(chat, text_to_send, parse_mode=ParseMode.HTML,
                                                  reply_markup=get_keyboard_message_start())
        if message:
            await save_message_id_to_user(message.message_id, user_id)
    except Exception as ER:
        my_logger.error(f'sending message or saving to db error {ER}')


async def create_meeting_message_from_web(bytes_string):
    try:
        string = bytes_string.decode('utf-8').replace("'", '"')
        my_data = json.loads(string)
        user_id = my_data.get('user_id')
        user_name = await get_name_from_db(user_id)
        history = await download_history(user_id)
        history = history[:5]
        history_prep = [(mes.get('is_answer'), mes.get('body'),) for mes in history]
        mask = await make_mask_to_web_messages(user_id, user_name)
        text = make_message_text(history_prep)
        text_to_send = md.text(mask, *text, sep='\n')
        chat = await check_user_chat(user_id)
    except Exception as ER:
        my_logger.error(f"preparing text error {ER}")
        return

    try:
        old_message_id = await get_message_id(user_id)
        if old_message_id:
            try:
                await bot.delete_message(chat, old_message_id)
            except:
                print('not')
        message: Message = await bot.send_message(chat, text_to_send, parse_mode=ParseMode.HTML,
                                                  reply_markup=get_keyboard_message_start())
        if message:
            await save_message_id_to_user(message.message_id, user_id)
    except Exception as ER:
        my_logger.error(f'sending message or saving to db error {ER}')
