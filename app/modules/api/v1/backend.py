from core.exceptions import ActionErrorException


class Backend(object):
    def __init__(self, app):
        self.controller = app.controller

    def add_group(self, user_id, group_data_list):
        try:
            cache = []
            for group in group_data_list:
                print(group)
                instances = group['instances']
                group['instances'] = [
                    {
                        'instance_id': inst[0],
                        'endpoint': inst[1]
                    }
                    for inst in instances
                ]
                group['user_id'] = user_id
                self.controller.create_group(group)
                cache.append(group)
            return True
        except ActionErrorException as e:
            # xoa toan bo group trong cache
            for g in cache:
                self.controller.drop_group(g)
            print(e)
            return False

    def get_groups(self, user_id):
        groups = self.controller.group.db_get_groups(user_id)
        return groups

    def get_group(self, group_dict):
        group = self.controller.group.db_get_group(group_dict)
        return group

    def update_group(self, group_dict):
        self.controller.update_group(group_dict)

    def drop_group(self, group_dict):
        self.controller.drop_group(group_dict)
