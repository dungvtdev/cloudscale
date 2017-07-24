import requests
from requests import exceptions

TIMEOUT = 20


def get(url, params=None):
    return requests.get(url, params=params, timeout=TIMEOUT)


def post(url, data=None):
    return requests.post(url, data=data, timeout=TIMEOUT)
