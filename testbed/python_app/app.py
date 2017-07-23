import json
import uuid
from wsgiref import simple_server

import falcon
import random

import os
myhost = os.uname()[1]


class StorageEngine(object):

    def get_things(self, marker, limit):
        return [{'id': str(uuid.uuid4()), 'color': 'green'}]

    def add_thing(self, thing):
        thing['id'] = str(uuid.uuid4())
        return thing


class ThingsResource(object):

    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, user_id):
        marker = req.get_param('marker') or ''
        limit = req.get_param_as_int('limit') or 50

        try:
            result = self.db.get_things(marker, limit)
        except Exception as ex:
            description = ('Aliens have attacked our base! We will '
                           'be back as soon as we fight them off. '
                           'We appreciate your patience.')

            raise falcon.HTTPServiceUnavailable(
                'Service Outage',
                description,
                30)

        # An alternative way of doing DRY serialization would be to
        # create a custom class that inherits from falcon.Request. This
        # class could, for example, have an additional 'doc' property
        # that would serialize to JSON under the covers.
        req.context['result'] = result

        resp.set_header('Powered-By', 'Falcon')
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'resp':'this is resp'})

    def on_post(self, req, resp, user_id):
        print(req.context)
        try:
            doc = req.context['doc']
        except KeyError:
            raise falcon.HTTPBadRequest(
                'Missing thing',
                'A thing must be submitted in the request body.')

        proper_thing = self.db.add_thing(doc)

        resp.status = falcon.HTTP_201
        resp.location = '/%s/things/%s' % (user_id, proper_thing['id'])


class CalcResource(object):
    def __init__(self, factor, loopcount, random_factor):
        self._factor = factor
        self._loopcount = loopcount
        self._random_factor = random_factor

        def mul_func(param):
            return reduce(lambda x, y: x*y, [i for i in range(param)])

        def sum_func(param):
            return sum([i for i in range(param)])

        def count_func(param):
            return sum([1 for i in range(param)])

        self._operators = {
            'mul': mul_func,
            'sum': sum_func,
            'count': count_func
        }

    def on_get(self, req, resp, calc):
        num = req.get_param_as_int('number', True)
        num = num * self._factor

        result = 0
        loop = self._random_factor(self._loopcount)
        for i in range(loop):
            result = self._operators[calc](num)

        resp.body = json.dumps({'result': result})


class StringMul(object):
    def __init__(self, loopcount):
        self._loopcount = loopcount

    def get(self, req, resp):
        str = req.get_param('str', True)
        num = req.get_param_as_int('count', True)

        result = ''
        for i in range(self._loopcount):
            result = ''
            for j in range(num):
                result = result + str

        resp.body = json.dumps({'result': result})


class PingHost(object):
    def on_get(self, req, resp):
        resp.body = json.dumps({'hostname': myhost})

# Configure your WSGI server.py to load "things.app" (app is a WSGI callable)
app = falcon.API()

db = StorageEngine()
things = ThingsResource(db)
app.add_route('/{user_id}/things', things)


def rand_factor(num):
    amount = int(0.15 * num)
    rnd = random.randint(-amount, amount)
    return num + rnd

calc = CalcResource(1, 30, rand_factor)
app.add_route('/calc/{calc}', calc)

str_mul = StringMul(30)
app.add_route('/str', str_mul)

app.add_route('/ping', PingHost())

if __name__ == '__main__':
    ip = '0.0.0.0'
    port = 8000

    httpd = simple_server.make_server(ip, port, app)
    print('Server serve on %s:%s' % (ip, port))

    httpd.serve_forever()