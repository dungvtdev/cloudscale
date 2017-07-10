

class MonitorController():
    def __init__(self, group_config, app):
        self.group_config = group_config

        endpoint = group_config['endpoint']
        to_db = group_config['to_db']
        metric = group_config['metric'][0]

        # 2 gia tri trong thuat toan, group khong the thay doi duoc
        epoch = 's'
        filter_setting = 'root_container_filter'

        app_config = app.config['MONITOR']
        self.interval_minute = app_config['interval_minute']

        read_plugin = getattr(app, app_config['parse_plugin'])
        def_read_config = app_config.get('parse', {})
        read_config = {
            'endpoint': endpoint,
            'db': def_read_config['db']
            'metric': metric,
            'epoch': epoch,
            'filter': filter_setting
        }

        self.reader = read_plugin.create(read_config)

        write_plugin = getattr(app, app_config['dump_plugin'])
        def_write_config = app_config.get('dump', {})
        write_config = {
            'max_fault_point': def_write_config.get('max_fault_point', 0),
            'endpoint': def_write_config['endpoint'],
            'metric': metric,
            'epoch': epoch,
            'tags': {
                'container_name': '/'
            },
            'db': to_db
        }
        self.writer = write_plugin.create(write_config)

    def init_data(self):
        # lay data hien co ghi vao csdl
        pass
