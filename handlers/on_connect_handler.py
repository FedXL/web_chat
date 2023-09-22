from aiohttp import request
from base.db_handlers import get_user_by_token
from base.redis_handlers import save_socket_user_mapping
from logs.logs import my_logger
from utils.token import check_token
from utils.utils3 import get_ip


async def check_cookie_main(request: request, soket_id):
    my_logger.debug('start')
    cookies = request.cookies
    print("[COCKIES]", cookies)
    if 'token' in cookies:
        my_logger.debug('token in cookies')
        token_value = cookies['token']
        is_valid = check_token(token_value)
        user_id = await get_user_by_token(token_value)
        await save_socket_user_mapping(user_id=user_id, socket_id=soket_id)
        if isinstance(is_valid, str):
            my_logger.debug('token expired  Refresh token or create new?')
            ip_request = get_ip(request)
            if ip_request == is_valid:
                my_logger.debug('the ip of token == ip of request so refresh token')

                return 'Refresh Token',  # and Download History'
            else:
                my_logger.debug('ip of token != ip of request so start create new user '
                                'branch (ask new username) ')
                return 'Ask UserName'
        elif not is_valid:
            my_logger.debug('Token is not valid , so ask new username and create new user')
            return 'Ask UserName',  # 'Create User', 'Create Token'
        elif is_valid:
            my_logger.debug('Token is valid, so download message history')
            return 'Download history',
        else:
            my_logger.error(f'is_valid {is_valid}')
    else:
        my_logger.debug('dont have token in cookies. asking user name')
        return 'Ask UserName',  # 'Create User', 'Create Token'


async def ask_username(ws):
    message = {
        "event": "ask_username",
    }
    await ws.send(message)
