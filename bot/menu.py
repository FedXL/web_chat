from aiogram import types


def get_keyboard_message_start():
    buttons = [
        types.InlineKeyboardButton(text="🗃", callback_data="message_menu"),
        types.InlineKeyboardButton(text="↕️️", callback_data="fast_answers_choice"),
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_fast_answer_menu():
    buttons = [
        types.InlineKeyboardButton(text="Ответы 🗣", callback_data="fast_answers_list"),
        types.InlineKeyboardButton(text="Карты 💳️", callback_data="fast_cards_list"),
        types.InlineKeyboardButton(text="🔼", callback_data="fast_back")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_menu_mess():
    buttons = [
        # types.InlineKeyboardButton(text="Забанить Гада 💔", callback_data="ban"),
        types.InlineKeyboardButton(text="✅ Завершено", callback_data='is_answered'),
        types.InlineKeyboardButton(text="🆘 Внимание", callback_data='is_not_answered'),
        # types.InlineKeyboardButton(text="🙏Спасибо🙏", callback_data='thanks'),
        types.InlineKeyboardButton(text="⚽️ Перекинуть", callback_data='change_channel'),
        types.InlineKeyboardButton(text="Full History", callback_data='full_history')
    ]
    keyword = types.InlineKeyboardMarkup(row_width=2)
    keyword.add(*buttons).\
        add(types.InlineKeyboardButton(text="↕️", callback_data="long_history")).\
        add(types.InlineKeyboardButton("🔼", callback_data="fast_back"))
    return keyword
