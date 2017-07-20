import falcon
from wsgiref import simple_server

from core import DependencyModule

from . import middlewares
from . import v1


class APIHandler(DependencyModule):
    __module_name__ = 'apihandler'

    def on_register_app(self, app):
        self._logger = app.logger
        self._conf = app.config['API']

        endpoints = self._get_endpoints()
        middlewares = self._get_middlewares()

        self.handler = falcon.API(middleware=middlewares)
        self.handler.add_error_handler(Exception, self._error_handler)

        for ver, ep in endpoints:
            if ver in self._conf['version']:
                for route, res in ep:
                    self.handler.add_route('/' + ver + route, res)

    def _get_endpoints(self):
        return [
            ('v1', v1.init_endpoints(self._app))
        ]

    def _get_middlewares(self):
        return [
            # middlewares.JwtAuth(),
            middlewares.RequireJSON(),
            middlewares.JSONTranslator(),
        ]

    def _error_handler(self, exc, request, response, params):
        """Handler error"""
        if isinstance(exc, falcon.HTTPError):
            raise exc
        self._logger.exception(exc)
        raise falcon.HTTPInternalServerError('Internal server error', exc)

    def listen(self):
        self._logger.info("*************************************"
                          "*******  Start API   ****************"
                          "*************************************")
        server_conf = self._conf

        host = server_conf['address']
        port = server_conf['port']
        msgtmpl = u'Serving on host %(host)s:%(port)s'
        self._logger.info(msgtmpl, {'host': host, 'port': port})
        # print(msgtmpl % {'host': host, 'port': port})

        httpd = simple_server.make_server(host, port, self.handler)
        httpd.serve_forever()
