import jwt
import base64
import json
from jwt.exceptions import DecodeError


class InvalidToken(Exception):
    pass


class AuthAgent(object):
    secret = 'secret'
    algorithm = 'HS256'

    def __init__(self, secret=None, algorithm=None):
        self.secret = secret or self.secret
        self.algorithm = algorithm or self.algorithm

    def get_token(self, payload):
        encoded = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return encoded

    def encode_token(self, token):
        parts = token.split('.')
        if len(parts) != 3:
            raise InvalidToken('Invalid Token parts, need 3 parts')

        b64header = parts[0]
        header = json.loads(base64.b64decode(b64header))
        if 'alg' not in header:
            raise InvalidToken('Token is not JWT token')
        alg = header['alg']
        try:
            return jwt.decode(token, self.secret, algorithms=[alg, ])
        except DecodeError:
            raise InvalidToken('Auth wrong')


class UserTokenAuth(AuthAgent):
    user_id = None

    def __init__(self, user_id=None, **kwargs):
        super(UserTokenAuth, self).__init__(**kwargs)
        self.user_id = user_id

    def create_token(self, user_id=None):
        id = user_id or self.user_id
        payload = {
            'user_id': id
        }
        return self.get_token(payload)

    def check_token(self, token):
        try:
            self.encode_token(token)
        except InvalidToken:
            return False
        return True

    def is_authen(self, token):
        return self.check_token(token)

    def is_own(self, token, user_id):
        if not self.is_authen(token):
            return False
        payload = self.encode_token(token)
        # print(payload)
        return payload.get('user_id', None) == user_id
