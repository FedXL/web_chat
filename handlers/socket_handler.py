import asyncio
import aiohttp
import aioredis
import async_timeout
from aiohttp import web
from base.db_handlers import create_user, associate_user_with_token, associate_user_with_socket, download_history, \
    refresh_old_token, remove_socket_from_db
from base.redis_handlers import save_socket_user_mapping, delete_socket_user_mapping, get_user_id_by_socket_id, \
     get_socket_id_by_user_id
from handlers.event_handlers import message_event_handler
from handlers.on_connect_handler import check_cookie_main
from handlers.pydentic_models import MessageLoad, HistoryLoad
from logs.logs import my_logger
from utils.token import get_name_from_token, create_token
from utils.utils3 import connect_to_redis_pubsub, get_ip

STOPWORD = "STOP"


async def redis_reader(channel: aioredis.client.PubSub, ws):
    my_logger.debug(f'open new redis listener with socket id: {str(id(ws))}')
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print('[info] we have a message')
                    try:
                        recieved_data = eval(message.get('data'))
                        recieved_mes = MessageLoad(**recieved_data)
                        text = recieved_mes.details.text
                        text = text.split(':', 1)[1]
                        recieved_mes.details.text = text
                        socket_id = await get_socket_id_by_user_id(recieved_mes.details.user_id)

                        if (int(id(ws))) == socket_id:
                            await ws.send_str(recieved_mes.model_dump_json())
                            my_logger.debug(f"sending to socket {socket_id} message = {recieved_mes.details.text}")
                        elif message["data"].decode() == STOPWORD:
                            print("(Reader) STOP")
                            break

                    except Exception as ER:
                        my_logger.error(f'problem: {ER}')

                await asyncio.sleep(0.5)
        except asyncio.TimeoutError:
            pass


async def websocket_handler(request):
    ws = aiohttp.web.WebSocketResponse(max_msg_size=10194304)
    await ws.prepare(request)
    socket_id = int(id(ws))
    user_ip = await get_ip(request)
    my_logger.debug(f'[INFO] new socket open: {socket_id} ,user ip {user_ip}')
    pubsub = await connect_to_redis_pubsub()
    task = asyncio.create_task(redis_reader(pubsub, ws))
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                load_data = msg.json()
                if msg.data == 'close':
                    await ws.close()
                elif load_data.get('event') == 'onconnect':
                    result = await check_cookie_main(request=request, soket_id=socket_id)
                    my_logger.debug(f'Check user result: {result}')
                    if 'Ask UserName' in result:
                        my_logger.debug(f'server: Asking username')
                        data = {'event': 'ask_username'}
                        await ws.send_json(data)
                    elif 'Refresh Token' in result:
                        my_logger.debug(f'[checker branch] start refresh token ')
                        try:
                            token = request.cookies.get('token')
                            name = get_name_from_token(token)
                            new_token = create_token(username=name, ip=user_ip)
                            is_refresh = await refresh_old_token(token, new_token)
                            data = {'event': 'refresh_token',
                                    'data': new_token,
                                    'is_refreshed': is_refresh}
                            await ws.send_json(data)
                        except Exception as ER:
                            my_logger.error(f"[checker branch] in refresh token checker branch {ER}")

                    elif 'Download history' in result:
                        my_logger.debug('[checker branch] start download history')
                        try:
                            id_user = await get_user_id_by_socket_id(socket_id=socket_id)
                            history = await download_history(user_id=id_user)
                            data = HistoryLoad(event='download_history', data=history)
                            await ws.send_json(data.model_dump())
                            my_logger.debug('the history was successfully send')
                        except Exception as ER:
                            my_logger.error(f'in download history checker branch {ER}')

                elif load_data.get('event') == 'username':
                    my_logger.debug(f"client sended username {load_data.get('username')}")
                    try:
                        username = load_data.get('username')
                        user_db_id = await create_user(name=username)
                        token = create_token(username=username, ip=user_ip)
                        await associate_user_with_token(user_id=user_db_id, token=token)
                        await associate_user_with_socket(user_id=user_db_id, socket_id=socket_id)
                        my_logger.debug("Username event: success")
                        data = {'event': 'new_token',
                                'data': token}
                        await ws.send_json(data)
                        await save_socket_user_mapping(socket_id=socket_id,
                                                       user_id=user_db_id)
                        my_logger.debug(f"server: sended  new token to user {username}")
                    except Exception as ER:
                        my_logger.error(f" in event username branch {ER}")

                elif load_data.get('event') == 'download_history':
                    my_logger.debug('start download history event branch')
                    try:
                        id_user: int = await get_user_id_by_socket_id(socket_id=socket_id)
                        history = await download_history(user_id=id_user)
                        data = {'event': 'download_history',
                                'data': history}

                        await ws.send_json(history)
                    except Exception as ER:
                        my_logger.error(f'in event download history branch {ER}')

                elif load_data.get('event') == 'PhotoOrPdf':
                    print('[INFO] download photo or pdf file ')

                elif load_data.get('event') == 'message':
                    try:
                        my_logger.debug('start event : message  from  message branch')
                        message_load = MessageLoad(**load_data)
                        message_load.details.user_id = await get_user_id_by_socket_id(socket_id=socket_id)
                        await message_event_handler(data=message_load, ws=ws)
                    except Exception as ER:
                        my_logger.error(f'in event message branch, {ER}')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                my_logger.error(f'[ERROR] Ошибка веб-сокета:  {msg}')
    except Exception as ER:
        my_logger.error(f'error in catch messages from socket {ER}')
    finally:
        my_logger.debug(f'close socket: killing redis {task},delete socket {socket_id} from DB')
        task.cancel()
        id_user = await get_user_id_by_socket_id(socket_id)
        await delete_socket_user_mapping(socket_id=socket_id, user_id=id_user)
        await remove_socket_from_db(socket_id)
    return ws
