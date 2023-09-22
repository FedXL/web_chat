import jwt
from config.config_app import sharable_secret
from utils.token import check_token


def test_create_token(token):
    assert isinstance(token, str)
    decoded_token = jwt.decode(token, sharable_secret, algorithms=["HS256"])
    assert decoded_token.get('name') == 'Fedor'
    assert decoded_token.get('ip') == '127.0.0.1'
    assert len(token.split('.')) == 3
    assert isinstance(decoded_token.get('exp'), int)


def test_check_token_with_wrong_secret(mocker, token):
    fake_secret = "wrong_secret"
    mocker.patch('config.config.sharable_secret', fake_secret)
    is_valid = check_token(token)
    assert not is_valid


def test_check_token_expiried_bad(mock_datetime_now_plus_8days, token):
    is_valid = check_token(token)
    assert isinstance(is_valid, str)


def test_check_token_expiried_good(mock_datetime_now_plus_2days, token):
    is_valid = check_token(token)
    assert is_valid
