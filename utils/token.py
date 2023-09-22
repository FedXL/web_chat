import datetime
import jwt
from logs.logs import my_logger


def create_token(ip, username):
    from config.config_app import sharable_secret
    my_logger.debug(f'start with name : {username} and ip {ip}')
    current_time = datetime.datetime.now()
    expiried_time = current_time + datetime.timedelta(days=6)
    token = jwt.encode({'name': username,
                        'ip': ip,
                        'exp': expiried_time},
                       key=sharable_secret,
                       algorithm='HS256')
    return token

def get_name_from_token(token:str) -> str:
    from config.config_app import sharable_secret
    try:
        decoded_token = jwt.decode(token, sharable_secret, algorithms=["HS256"])
        name = decoded_token.get('name')
        return name
    except Exception:
        my_logger.error('cannot to decode token')
        raise BrokenPipeError ('cannot to decode token ')

def check_token(token:str) -> bool | str:
    my_logger.debug('start')
    from config.config_app import sharable_secret
    today = datetime.datetime.now()

    try:
        decoded_token = jwt.decode(token, sharable_secret, algorithms=["HS256"])
        expiried_time=decoded_token.get('exp')
        expiried_time = datetime.datetime.fromtimestamp(expiried_time)
        my_logger.debug('token is valid. Start check for expiried data')

        if expiried_time >= today:

            my_logger.debug('Token is good')
            return True
        else:
            my_logger.debug(f"expiried token, ip {decoded_token.get('ip')}")
            return decoded_token.get('ip')
    except Exception as ER:
        print(ER)
        my_logger.debug(f'fraud token')
        return False


