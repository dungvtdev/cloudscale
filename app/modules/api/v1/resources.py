import falcon

def init_route(app):

    controller = app.controller

    class ResourceGroups(object):
        def on_get(self, req, resp, user_id):
            pass

        def on_post(self, req, resp, user_id):
            pass


    class ResourceGroup(object):
        def on_delete(self, req, resp, user_id, group_id):
            pass

        def on_get(self, req, resp, user_id, group_id):
            pass


    class ResourceGroupAction(object):
        post_map = ['update_group', 'purge_group', ]
        get_map = ['status', ]

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

        def _update_group_action(self, req, resp, user_id, group_id):
            pass

        def _purge_group_action(self, req, resp, user_id, group_id):
            pass

        def _status_action(self, req, resp, user_id, group_id):
            pass


    class ResourceInstances(object):
        def on_get(self, req, resp, user_id):
            pass


    routes = [
        ('users/{user_id}/groups', ResourceGroups()),
        ('users/{user_id}/groups/{group_id}', ResourceGroup()),
        ('users/{user_id}/groups/{group_id}/{action}', ResourceGroupAction()),
        ('users/{user_id}/vms', ResourceInstances())
    ]

    return routes
