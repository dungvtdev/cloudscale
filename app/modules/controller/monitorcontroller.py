from core import seriesutils as su


class MonitorController():
    def __init__(self, group_config, app):
        self.group_config = group_config
        self.logger = app.logger

        endpoint = group_config['endpoint']
        to_db = group_config['to_db']
        metric = group_config['metric'][0]
        self.interval_minute = group_config['interval_minute']

        # 2 gia tri trong thuat toan, group khong the thay doi duoc
        epoch = 's'
        filter_setting = 'root_container_filter'

        app_config = app.config['MONITOR']
        self.max_batch_size = app_config['max_batch_size']
        self.max_fault_point = def_write_config.get('max_fault_point', 0)

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
            'endpoint': def_write_config['endpoint'],
            'metric': metric,
            'epoch': epoch,
            'tags': {
                'container_name': '/'
            },
            'db': to_db
        }
        self.writer = write_plugin.create(write_config)

    @property
    def data_total(self):
        return self.data_total

    def init_data(self):
        # lay data hien co ghi vao csdl
        time_to = None
        max_batch_size = self.max_batch_size
        interval_minute = self.interval_minute
        max_fault_point = self.max_fault_point

        time_from_begin = None
        cache = []

        self.data_total = 0

        while(True):
            try:
                timevalues = self.reader.read(time_lenth=max_batch_size,
                                              time_to=time_to)
                if not timevalues:
                    break

                last = timevalues[-1][0]
                time_to = last

                if not time_from_begin:
                    time_from_begin = last

                df = su.minutevaluepair_to_pdseries(timevalues)
                df = su.resample(df, self.interval_minute)
                newest = su.get_newestseries(df, max_fault_point)

                # cache lai de dung ngay khi du dieu kien train data
                cache.append(newest)

                # convert to time value pair to write
                self.write_data_series(newest, last)

                is_finish = len(df) != len(newest)
                if(is_finish):
                    break
            except Exception as e:
                if 'Got Data is None' in e.message:
                    break
                else:
                    raise e

        # khi lay xong du lieu, check lai do dai du lieu xem the nao
        first_interval = interval_minute

        try:
            tv = self.reader.read(time_from=time_from_begin)
            if tv:
                last_tv = tv[-1][0]
                amount_time = last_tv - time_from_begin
                delta = amount_time % interval_minute
                first_interval = self.interval_minute - delta
                if amount_time >= interval_minute:
                    # cache lai du lieu
                    df = su.minutevaluepair_to_pdseries(timevalues)
                    df = su.resample(df, self.interval_minute)
                    newest = su.get_newestseries(df, max_fault_point)
                    # bo di phan tu cuoi vi chua du chu ky
                    newest = newest[:len(newest) - 1]
                    cache = [newest, ] + cache
                    self.write_data_series(newest, last)
        except Exception as e:
            pass

        # tinh tong so point thu duoc
        total = sum(len(c) for c in cache)
        self.data_total = total

        self.logger.info('Get %s point from %s' %
                         (total, self.group_config['endpoint']))

        return first_interval

    def write_data_series(self, series, last):
        begin = last - len(series) + 1
        values = [((begin + i) * 1000000000 * 60, series[i])
                  for i in range(len(newest))]
        self.writer.write(values)

    def get_last_one(self):
        values = self.reader.read(time_length=self.interval_minute)
        if values:
            self.data_total = self.data_total + 1
            t = values[-1][0]
            v = sum(v[1] for v in values) / len(values)
            return t, v
        return None, None
