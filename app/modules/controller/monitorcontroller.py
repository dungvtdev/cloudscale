from core import seriesutils as su
from core.exceptions import InstanceNotValid, ServiceIOException, BadInputParams
from requests.exceptions import ConnectionError, Timeout


class MonitorController():
    def __init__(self, group_config, app):
        self.group_config = group_config
        self.logger = app.logger
        self.logname = "Group %s" % group_config['name']

        endpoint = group_config['endpoint']
        # to_db = group_config['to_db']
        metric = group_config['metric']
        self.interval_minute = group_config['interval_minute']

        # 2 gia tri trong thuat toan, group khong the thay doi duoc
        epoch = 'm'
        filter_setting = 'root_container_filter'

        app_config = app.config['MONITOR']
        self.max_batch_size = app_config['max_batch_size']
        self.max_fault_point = app_config.get('max_fault_point', 0)

        read_plugin_config = app_config['read_plugin']
        read_plugin = getattr(app, read_plugin_config['plugin'])
        def_read_config = read_plugin_config['config']
        read_config = {
            'endpoint': endpoint,
            'db': def_read_config['db'],
            'metric': metric,
            'epoch': epoch,
            'filter': filter_setting
        }

        self.reader = read_plugin.create(read_config)

        cache_plugin_config = app_config['cache_plugin']
        cache_plugin = getattr(app, cache_plugin_config['plugin'])
        def_cache_config = cache_plugin_config['config']
        db_name = def_cache_config['db']
        if '%s' in db_name:
            db_name = db_name % group_config['name']
        cache_config = {
            'endpoint': def_cache_config['endpoint'],
            'metric': metric,
            'epoch': epoch,
            'tags': {
                'container_name': '/'
            },
            'db': db_name
        }
        self.cacher = cache_plugin.create(cache_config)

    @property
    def data_total(self):
        return self.data_total

    def init_data(self):
        if self.interval_minute > 1:
            return self.init_data_interval_large()
        elif self.interval_minute == 1:
            return self.init_data_interval_one()

    def init_data_interval_one(self):
        time_to = None
        max_batch_size = self.max_batch_size
        first_interval = 1
        max_fault_point = self.max_fault_point

        time_from_begin = None
        is_last_chunk = True
        cache = []

        self.data_total = 0

        max_time_length = max_batch_size / 47

        while True:
            try:
                timevalues = self.reader.read(time_length=max_time_length,
                                              time_to=time_to)
                if not timevalues:
                    break

                df = su.minutevaluepair_to_pdseries(timevalues)
                df = su.resample(df, self.interval_minute)
                newest = su.get_newestseries(df, max_fault_point)
                if newest is not None and len(newest) > 0:
                    newest = su.force_positive(newest)

                is_finish = len(df) != len(newest)

                last = timevalues[-1][0]

                if is_last_chunk:
                    is_last_chunk = False
                    # cat dau duoi
                    # last = timevalues[-1][0]
                    # la time cuoi cung cua chunk cuoi cung
                    time_from_begin = last

                    time_to = timevalues[0][0]
                else:
                    time_to = time_to - len(newest)
                # cache lai de dung ngay khi du dieu kien train data
                cache.append(newest)

                # convert to time value pair to write
                self.write_data_series(newest, last, 1)

                if is_finish:
                    break
            except (ConnectionError, Timeout) as e:
                raise InstanceNotValid()
            except Exception as e:
                if 'Got Data is None' in e.message:
                    break
                else:
                    raise e

        last_time = time_from_begin

        try:
            tv = self.reader.read(time_from=time_from_begin)
            if tv:
                last_tv = tv[-1][0]
                # cache lai du lieu
                df = su.minutevaluepair_to_pdseries(tv)
                # last = df[-1][0]
                df = su.resample(df, self.interval_minute)
                newest = su.get_newestseries(df, max_fault_point)
                if newest is not None and len(newest) > 0:
                    newest = su.force_positive(newest)

                if len(newest) > 0 and time_from_begin == tv[0][0]:
                    newest = newest[1:]

                cache = [newest, ] + cache
                # last = newest[-1][0]
                last = time_from_begin + len(newest) - 1
                self.write_data_series(newest, last, 1)

                last_time = last
            # ghi lai last time value
            # print(last_time)
            self.write_cache_value('last_time', last_time)
            # self.cacher.write_value('last_time', last_time)
        except (ConnectionError, Timeout) as e:
            raise InstanceNotValid()
        except Exception as e:
            if 'Got Data is None' not in e.message:
                raise e

        cache = cache[::-1]
        # tinh tong so point thu duoc
        total = sum(len(c) for c in cache)
        self.data_total = total

        self.logger.info('Get %s point from %s' %
                         (total, self.group_config['endpoint']))

        # print(total)
        # with open('/home/dungvt/read.cache', 'w') as f:
        #     for c in cache:
        #         f.write(str(c))
        return {
            'first_interval': first_interval,
            'total': total,
            'cache': cache
        }

    def init_data_interval_large(self):
        # lay data hien co ghi vao csdl
        time_to = None
        max_batch_size = self.max_batch_size
        interval_minute = self.interval_minute
        max_fault_point = self.max_fault_point

        time_from_begin = None
        is_last_chunk = True
        cache = []

        self.data_total = 0

        max_time_length = max_batch_size / 47
        while True:
            try:
                timevalues = self.reader.read(time_length=max_time_length,
                                              time_to=time_to)
                if not timevalues:
                    break

                df = su.minutevaluepair_to_pdseries(timevalues)
                df = su.resample(df, self.interval_minute)
                newest = su.get_newestseries(df, max_fault_point)
                if newest is not None and len(newest) > 0:
                    newest = su.force_positive(newest)
                is_finish = len(df) != len(newest)

                if len(newest) <= 3:
                    raise BadInputParams('too short data')

                if is_last_chunk:
                    is_last_chunk = False
                    # cat dau duoi
                    newest = newest[1:len(newest) - 1]
                    if newest is not None and len(newest) > 0:
                        newest = su.force_positive(newest)

                    last = timevalues[-1][0]
                    # time cua chunk cuoi cung cua newest
                    temp_t = (int(last / interval_minute) - 1) * interval_minute
                    # la time cuoi cung cua chunk cuoi cung
                    time_from_begin = temp_t + interval_minute
                    # la T - 1, T la time cua chunk dau tien cua newest
                    time_to = temp_t - (len(newest) - 1) * interval_minute - 1
                    # max_time_length chia het cho interval_minute
                    max_time_length = max_time_length - max_time_length % interval_minute
                else:
                    time_to = time_to - len(newest) * interval_minute
                    last = timevalues[-1][0]
                    last = last - last % interval_minute
                # cache lai de dung ngay khi du dieu kien train data
                cache.append(newest)

                # convert to time value pair to write
                self.write_data_series(newest, last, self.interval_minute)

                if is_finish:
                    break
            except (ConnectionError, Timeout) as e:
                raise InstanceNotValid()
            except Exception as e:
                if 'Got Data is None' in e.message:
                    break
                else:
                    raise e

        # kiem tra vong lap truoc co ok khong
        if not cache:
            raise BadInputParams('too short data')

        # khi lay xong du lieu, check lai do dai du lieu xem the nao
        first_interval = interval_minute

        last_time = time_from_begin

        try:
            tv = self.reader.read(time_from=time_from_begin)
            if tv:
                last_tv = tv[-1][0]
                amount_time = last_tv - time_from_begin + 1
                delta = amount_time % interval_minute
                extra = int(amount_time / interval_minute)
                first_interval = self.interval_minute - delta
                if extra > 0:
                    # cache lai du lieu
                    df = su.minutevaluepair_to_pdseries(tv)
                    # last = df[-1][0]
                    df = su.resample(df, self.interval_minute)
                    newest = su.get_newestseries(df, max_fault_point)
                    # truong hop interval_minute > 1, delta la phan thua ra khong du chu ky
                    # neu interval_minute = 1 thi delta = 0
                    if delta > 0:
                        newest = newest[:len(newest) - 1]
                    cache = [newest, ] + cache
                    # last = newest[-1][0]
                    last = time_from_begin + extra * interval_minute
                    self.write_data_series(newest, last, self.interval_minute)

                    last_time = last
            # ghi lai last time value
            # print(last_time)
            self.write_cache_value('last_time', last_time)
            # self.cacher.write_value('last_time', last_time)
        except (ConnectionError, Timeout) as e:
            raise InstanceNotValid()
        except Exception as e:
            if 'Got Data is None' not in e.message:
                raise e

        cache = cache[::-1]
        # tinh tong so point thu duoc
        total = sum(len(c) for c in cache)
        self.data_total = total

        self.logger.info('%s Get %s point from %s' %
                         (self.logname, total, self.group_config['endpoint']))

        # print(total)
        # with open('/home/dungvt/read.cache', 'w') as f:
        #     for c in cache:
        #         f.write(str(c))
        return {
            'first_interval': first_interval,
            'total': total,
            'cache': cache
        }

    def write_data_series(self, series, last, step):
        begin = last - len(series) * step + 1
        values = [((begin + i * step) * 1000000000 * 60, series[i])
                  for i in range(len(series))]
        try:
            self.cacher.write(values)
        except (ConnectionError, Timeout):
            raise ServiceIOException()

    def write_cache_value(self, key, value):
        try:
            self.cacher.write_value(key, value)
        except (ConnectionError, Timeout):
            raise ServiceIOException()

    def read_cache_value(self, key):
        try:
            return self.cacher.read_value(key)
        except (ConnectionError, Timeout):
            raise ServiceIOException()

    def get_data_series(self):
        # max_time_length = self.max_batch_size * self.interval_minute
        max_batch_size = 1000
        max_time_length = max_batch_size * self.interval_minute

        # TODO can than cho nay neu khong read duoc value
        try:
            time_to = int(self.read_cache_value('last_time'))
        except:
            time_to = None

        accum = []
        while True:
            try:
                values = self.cacher.read(
                    time_to=time_to, time_length=max_time_length)

                if not values:
                    break

                # tru 1 cung duoc vi so sanh <= time_to
                time_to = values[0][0] - 1

                accum.append(values)

                is_finish = len(values) < max_batch_size

                if is_finish:
                    break
            except Exception as e:
                if 'Got Data is None' in e.message:
                    break
                else:
                    raise e
        accum = accum[::-1]

        # total = sum(len(a) for a in accum)
        # print(total)
        # with open('/home/dungvt/read2.cache', 'w') as f:
        #     for c in accum:
        #         f.write(str(c))

        return accum

    def get_last_one(self):
        try:
            values = self.reader.read(time_length=self.interval_minute)
            if values:
                self.data_total = self.data_total + 1
                t = values[-1][0]
                t = t - t % self.interval_minute
                v = sum(v[1] for v in values) / len(values)

                # write to database
                t_ns = t * 1000000000 * 60
                self.cacher.write([(t_ns, v), ])

                self.write_cache_value('last_time', t)

                return t, v
            return None, None
        except (ConnectionError, Timeout) as e:
            raise InstanceNotValid()
