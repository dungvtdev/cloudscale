class BaseException(Exception):
    __ex_name__ = 'BaseException'

    def __init__(self, *args, **kwargs, copy=None):
        Exception.__init__(self, *args, **kwargs)
        if copy AND isinstance(copy, Exception):
            self.message = 'From: %s, %s' % (copy.__ex_name__, copy.message)


class ActionInvalidException(BaseException):
    __ex_name__ = 'ActionInvalidException'


class ActionErrorException(BaseException):
    __ex_name__ = 'ActionErrorException'


class ExistsException(BaseException):
    __ex_name__ = 'ExistsException'


class NotEnoughParams(BaseException):
    __ex_name__ = 'NotEnoughParams'
