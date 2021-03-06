import falcon
from .backend import Backend


def init_route(app):
    # controller = app.controller
    backend = Backend(app)

    class ResourceGroups(object):
        def on_get(self, req, resp, user_id):
            groups = backend.get_groups(user_id) or []
            req.context['result'] = {
                'groups': groups
            }

        def on_post(self, req, resp, user_id):
            body = req.context['doc']
            if 'groups' not in body:
                raise falcon.HTTP_BAD_REQUEST(
                    "Create group must have 'group' in body")

            rl = backend.add_group(user_id, body['groups'])
            if not rl:
                raise falcon.HTTP_BAD_REQUEST('Can\'t create group')

    class ResourceGroup(object):
        def on_delete(self, req, resp, user_id, id):
            backend.drop_group({'id': id})

        def on_get(self, req, resp, user_id, id):
            group = backend.get_group({'id': id})
            groups = [group, ] if group else []
            req.context['result'] = {
                'groups': groups
            }

    class ResourceGroupAction(object):
        post_map = ['update_group', 'purge_group', ]
        get_map = ['status', 'log']

        def on_post(self, req, resp, user_id, id, action):
            if action in self.post_map:
                fn = getattr(self, '_{action}_action'.format(action=action))
                fn(req, resp, user_id, id)
            else:
                raise falcon.HTTPBadRequest('Method post not allow')

        def on_get(self, req, resp, user_id, id, action):
            if action in self.get_map:
                fn = getattr(self, '_{action}_action'.format(action=action))
                fn(req, resp, user_id, id)
            else:
                raise falcon.HTTPBadRequest('Method get not allow')

        def _update_group_action(self, req, resp, user_id, id):
            # cho nay confuse giua id va group_id nen chua check
            body = req.context['doc']
            try:
                group = body['groups'][0]
                backend.update_group(group)
            except:
                raise falcon.HTTPBadRequest('update none group')

        def _purge_group_action(self, req, resp, user_id, id):
            pass

        def _status_action(self, req, resp, user_id, id):
            pass

        def _log_action(self, req, resp, user_id, id):
            group = backend.get_group({'id': id})
            g_log = backend.get_group_log(group)
            req.context['result'] = {
                'log': g_log
            }

    class ResourceInstances(object):
        def on_get(self, req, resp, user_id):
            pass

    routes = [
        ('/users/{user_id}/groups', ResourceGroups()),
        ('/users/{user_id}/groups/{id}', ResourceGroup()),
        ('/users/{user_id}/groups/{id}/{action}', ResourceGroupAction()),
        ('/users/{user_id}/vms', ResourceInstances())
    ]

    return routes
