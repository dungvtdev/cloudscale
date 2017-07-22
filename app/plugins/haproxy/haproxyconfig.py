from pyhaproxy.parse import Parser
from pyhaproxy.render import Render
from pyhaproxy import config
from subprocess import call
from core import DependencyModule

# from core.exceptions import ExistsException

frontend_prefix = 'localnodes'
backend_prefix = 'backendnodes'


class HAProxyCtrl(DependencyModule):
    __module_name__ = 'haproxy'

    def on_register_app(self, app):
        self.cf_path = app.config['LOADBALANCER']['config_path']

    def add_server(self, endpoint_addr, endpoint_port, port):
        endpoint_port = str(endpoint_port)
        port = str(port)

        cfg_parser = Parser(self.cf_path)
        configuration = cfg_parser.build_configuration()

        backend = self.get_backend(configuration, port)
        servers = backend.servers()

        # check server
        exist_server = next((s for s in servers if s.host == endpoint_addr and s.port == endpoint_port), None)
        if exist_server is None:
            # get available name
            idx = max(
                [int(c[1]) for c in [s.name.split('_') for s in servers] if
                 len(c) == 2 and c[0] == 'web' and c[1].isdigit()] or [0, ])
            idx = idx + 1
            sname = 'web_%s' % idx
            backend.servers().append(config.Server(sname, endpoint_addr, endpoint_port, ['check', ]))

        cfg_render = Render(configuration)
        cfg_render.dumps_to(self.cf_path)

        HAProxyCtrl.restart_service()

    def remove_server(self, endpoint_addr, endpoint_port, port):
        endpoint_port = str(endpoint_port)
        port = str(port)

        cfg_parser = Parser(self.cf_path)
        configuration = cfg_parser.build_configuration()

        name = HAProxyCtrl.get_backend_name(port)
        backend = configuration.backend(name)
        if not backend:
            return

        servers = backend.servers()

        # check server
        exist_server = next((s for s in servers if s.host == endpoint_addr and s.port == endpoint_port), None)
        if exist_server is not None:
            servers.remove(exist_server)

        # check server empty
        if len(servers) == 0:
            # xoa backend va frontend
            configuration.backends.remove(backend)

            frontend_name = HAProxyCtrl.get_frontend_name(port)
            frontend = configuration.frontend(frontend_name)
            if frontend:
                configuration.frontends.remove(frontend)

        cfg_render = Render(configuration)
        cfg_render.dumps_to(self.cf_path)

        HAProxyCtrl.restart_service()

    def get_backend(self, configuration, port):
        # cfg_parser = Parser(cf_path)
        # configuration = cfg_parser.build_configuration()

        name = HAProxyCtrl.get_frontend_name(port)
        exist_frontend = configuration.frontend(name)
        if exist_frontend:
            backend_name = exist_frontend.config_block['usebackends'][0].backend_name
            return configuration.backend(backend_name)

        backend_name = HAProxyCtrl.get_backend_name(port)
        exist_backend = configuration.backend(backend_name)
        if exist_backend:
            newbackend = exist_backend
        else:
            newbackend = config.Backend(backend_name, {
                'configs': [
                    ('mode', 'http'),
                    ('balance', 'roundrobin')
                ],
                'options': [
                    ('forwardfor', '')
                ],
                'servers': []
            })
            configuration.backends.append(newbackend)

        usebackend = config.UseBackend(newbackend.name, "", "", True)
        frontends = configuration.frontends
        newfrontend = config.Frontend(name, '*', port, {
            'usebackends': [usebackend, ],
            'binds': [config.Bind('*', port, None), ],
            'configs': [
                ('mode', 'http')
            ],
            'default_backend': []
        })
        frontends.append(newfrontend)
        return newbackend

    @classmethod
    def restart_service(cls):
        call(['service', 'haproxy', 'restart'])

    @classmethod
    def get_frontend_name(cls, port):
        return '%s%s' % (frontend_prefix, port)

    @classmethod
    def get_backend_name(cls, port):
        return '%s%s' % (backend_prefix, port)

# if __name__ == '__main__':
#     haproxy = HAProxyCtrl()
#     # haproxy.add_server('192.168.1.223', 8000, 81)
#     haproxy.remove_server('192.168.1.223', 8000, 81)
#     haproxy.add_server('192.168.1.223', 8000, 81)
#     # haproxy.remove_server('192.168.1.223', 8000, 81)
#     # haproxy.remove_server('192.168.1.22', 8000, 81)
