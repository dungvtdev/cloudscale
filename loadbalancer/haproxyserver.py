from pyhaproxy.parse import Parser
from pyhaproxy.render import Render
from pyhaproxy import config
from subprocess import call
import falcon
import json
from wsgiref import simple_server

cf_path = '/etc/haproxy/haproxy.cfg'


class LoadBalancer():
    _instance = None

    def __init__(self):
        self._count = 0

    @classmethod
    def default(cls):
        if LoadBalancer._instance is None:
            LoadBalancer._instance = LoadBalancer()
        return LoadBalancer._instance

    def add_servers(self, servers):
        if not servers:
            return
        print('Add servers %s' % servers)
        self._add_servers_config(servers)
        self._restart_service()

    def remove_servers(self, servers):
        if not servers:
            return
        self._remove_servers_config(servers)
        self._restart_service()

    def _add_servers_config(self, servers):
        cfg_parser = Parser(cf_path)
        configuration = cfg_parser.build_configuration()

        backend = configuration.backend('osnodes')

        for server in servers:
            sname = 'web%s' % self._count
            self._count = self._count + 1

            backend.servers().append(config.Server(sname, server[0], server[1], ['check', ]))

        cfg_render = Render(configuration)
        cfg_render.dumps_to(cf_path)

    def _remove_servers_config(self, servers):
        cfg_parser = Parser(cf_path)
        configuration = cfg_parser.build_configuration()

        backend = configuration.backend('osnodes')

        map = ['%s:%s' % (s[0], s[1]) for s in servers]
        remove_server_objs = [s for s in backend.servers() \
                              if '%s:%s' % (s.host, s.port) in map]

        for rm_server in remove_server_objs:
            backend.servers().remove(rm_server)

        cfg_render = Render(configuration)
        cfg_render.dumps_to(cf_path)

    def _restart_service(self):
        call(['service', 'haproxy', 'restart'])


def test():
    lb = LoadBalancer.default()
    # lb.remove_servers([('192.168.122.188','8888')])
    # lb.add_servers([('192.168.122.188','8888')])


class HandleResource():
    def on_post(self, req, resp):
        print(req.host)
        body = req.stream.read()
        data = json.loads(body)['servers']

        ip = req.remote_addr
        for d in data:
            d[0] = ip
        lb = LoadBalancer.default()
        lb.add_servers(data)

def server_up():
    app = falcon.API()
    app.add_route('/add_servers', HandleResource())
    port = 8080
    httpd = simple_server.make_server('0.0.0.0', port, app)
    print('Server serve at 0.0.0.0:%s' % port)
    httpd.serve_forever()

if __name__ == '__main__':
    server_up()
