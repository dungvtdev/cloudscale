class BaseWrapperException(Exception):
    __ex_name__ = 'BaseWrapperException'

    def __init__(self, copy=None, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        if copy and isinstance(copy, Exception):
            self.message = 'From: %s, %s' % (copy.__ex_name__, copy.message)


class ActionInvalidException(BaseWrapperException):
    __ex_name__ = 'ActionInvalidException'


class ActionErrorException(BaseWrapperException):
    __ex_name__ = 'ActionErrorException'


class ExistsException(BaseWrapperException):
    __ex_name__ = 'ExistsException'


class NotEnoughParams(BaseWrapperException):
    __ex_name__ = 'NotEnoughParams'
