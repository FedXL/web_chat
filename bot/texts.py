import re
import aiogram.utils.markdown as md
from aiogram import types
from aiogram.types import CallbackQuery


def make_user_info_report(query: CallbackQuery, order_id=None) -> md.text():
    user_id = query.from_user.id
    user_first_name = query.from_user.first_name
    user_second_name = query.from_user.last_name
    username = query.from_user.username

    result = md.text(
        md.text(f" #{order_id}"),
        md.text(f"Type: <b>{query.data}</b>"),
        md.text(f"User: ", md.hlink(f"#ID_{user_id}", f"tg://user?id={user_id}")),
        md.text(f"First Name: {user_first_name}"),
        md.text(f"Second Name: {user_second_name}"),
        md.text(f"UserName :  @{username}"),
        sep="\n"
    )

    return result


def make_user_info_report_from_message(message: types.Message):
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_second_name = message.from_user.last_name
    result = md.text(
        md.text(f"#ID_{user_id}"),
        md.text(f"First Name: {user_first_name}"),
        f"|",
        md.text(f"Second Name: {user_second_name}"),
        sep="\n"
    )
    return result



# def get_mask_from_message(text_to_parce):
#     """ маска со стороны менеджеров """
#     result = []
#     id = get_id_from_text(text_to_parce)
#     text_to_parce = text_to_parce.split("\n")
#     result.append(f"#ID_{id}")
#     result.append(text_to_parce[1])
#     result = add_orders_to_mask(id, result)
#     return result




async def make_mask_to_web_messages(user_id, user_name) -> md.text():
    """это делает маску со стороны юзеров"""
    result = [
        md.text(f"#WEB_{user_id}"),
        md.text(f"{user_name}",
                )]
    result = md.text(*result, sep="\n")
    return result


def order_answer_vocabulary(income, order_id):
    match income:
        case 'KAZ_ORDER_LINKS':
            text = ['Вариант 1', f'Заказ через Казахстан №{order_id}', 'ссылки']
        case 'KAZ_ORDER_CABINET':
            text = ['Вариант 1', f'Заказ через Казахстан №{order_id}', 'доступ в кабинет']
        case 'TRADEINN':
            text = ['Вариант 2', f'Заказ через TradeInn №{order_id}']
        case 'PAYMENT':
            text = ['Вариант 3', f'Выкуп через посредника №{order_id}']
    return text





def get_vaflalist(pos=1):
    if pos == 1:
        result = ('первая',
                  'вторая',
                  'третья',
                  'четвертая',
                  'пятая',
                  'шестая',
                  'седьмая',
                  'восьмая',
                  'девятая',
                  'десятая',
                  'одиннадцатая',
                  'двенадцатая',
                  'тринадцатая',
                  'четырнадцатая',
                  'пятнадцатая')
    elif pos == 2:
        result = ('первой',
                  'второй',
                  'третьей',
                  'четвертой',
                  'пятой',
                  'шестой',
                  'седьмой',
                  'восьмой',
                  'девятой',
                  'десятой',
                  'одиннадцатой',
                  'двенадцатой',
                  'тринадцатой',
                  'четырнадцатой',
                  'пятнадцатой',)
    return result


def get_additional_from_proxi(data):
    """Не помню уже видимо что то связанное с созданием текста в ордере"""
    print("data " * 10, data, sep="\n")
    addition = []
    hrefs = [data.get(key) for key in [('href_' + str(key)) for key in
                                       [i for i in range(1, data.get('num') + 1)]]]
    comments = [data.get(key) for key in
                [('comment_' + str(key)) for key in
                 [i for i in range(1, data.get('num') + 1)]]]
    link = iter(make_links_info_text(hrefs))
    comment = iter(comments)
    addition.append(md.text('shop: ', f"<code>{data['shop']}</code>"))
    for x in hrefs:
        new = md.text(next(link), ": ", f"{next(comment)}")
        addition.append(new)
    return addition


def get_id_from_text(text):
    id = re.search(r"#ID_(\d+)", text)
    if id:
        return id.group(1)
    else:
        return None

def get_web_id_from_text(text):
    id = re.search(r"#WEB_(\d+)", text)
    if id:
        return id.group(1)
    else:
        return None




def make_message_text(message: list) -> md.text():
    message = check_lenght(message)
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer, body in before:
        if is_answer:
            pointer = "✅"
            if len(body) > 50:
                body = str(body[:50]) + "..."
        else:
            pointer = "🆘"

        result.append(md.text(pointer, body, sep=" "))
        result.append(md.text(" "))

    for is_answer, body in after:
        if is_answer:
            pointer = '👉'
        else:
            pointer = '👈'
        if len(str(body)) >= 80:
            insert_text = str(body)[:60] + "..."
        else:
            insert_text = str(body)
        result.append(md.text(pointer, insert_text, sep=" "))
    return result


def check_lenght(text: list) -> list:
    while len(str(text)) > 4000:
        text.pop()
    return text


def make_message_text_full(message: list) -> md.text():
    message = check_lenght(message)
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer, time, body in before:
        if is_answer:
            pointer = "✅"
        else:
            pointer = "🆘"
        result.append(md.text(pointer, time, body, sep=" "))
        result.append(md.text(" "))
    for is_answer, time, body in after:
        if is_answer:
            pointer = ''
        else:
            pointer = '👈'
        result.append(md.text(pointer, time, body, sep=" "))
    return result
