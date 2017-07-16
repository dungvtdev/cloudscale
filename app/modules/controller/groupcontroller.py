import thread
import threading
import copy

# from threading import Lock
import time
from core.exceptions import NotEnoughParams, ExistsException, \
    InstanceNotValid, ServiceIOException
from . import MonitorController
from . import ForecastCpuController
from core.seriesutils import join_series

# WAIT_FOR_TRAIN_STATE = 'training'
# PREDICT_STATE = 'predicting'

forecast_map = {
    'cpu_usage_total': ForecastCpuController
}


class GroupController(threading.Thread):
    WARM_UP_TIME_SECS = 240

    def __init__(self, app, group_dict):
        threading.Thread.__init__(self)

        self.app = app
        self.logname = group_dict['name']

        self.is_running = False

        self.groupservice = self.app.grouputils

        if not group_dict.get('instances', None):
            raise NotEnoughParams('Create new group must containt vms')
        # tao group
        group_dict = self.groupservice.db_create_group(group_dict)

        # tao cac vm lien quan
        for vm in group_dict['instances']:
            vm['is_monitoring'] = False
            vm['user_id'] = group_dict['user_id']

        try:
            vm_dicts = self.groupservice.db_create_vms_onlynew(
                group_dict['instances'])
        except ExistsException as e:
            # xoa group da tao
            self.groupservice.db_drop_group(group_dict)
            raise e

        group_dict['instances'] = vm_dicts

        self.monitorcontroller = None

        # co thread scale anh huong toi self.data, self._last_scale_time,
        # nhung dong bo la khong can thiet vi khong can duyet self.data va
        # self._last_scale_time chi luu thoi diem cuoi cung scale
        self.data = group_dict

        # self._last_scale_time = 0
        # khong dung Boolean vi co the co nhieu thread cung chay, thuc ra
        # khong can dong bo nhung van la giai phap an toan
        # self._scaling_threads = []

        self.wait_cycle_training = self.data['data_length']
        self.wait_cycle_update = self.data['update_in_time']

        self.forecast_model = None
        self.scalecontroller = self.create_scalecontroller()

        # self.local_timestamp = 0

        self.setup_cache()

    def setup_cache(self):
        # setup cache
        cache_config = self.app.config['GROUPCACHE']['cache_plugin']
        cache_plugin = getattr(self.app, cache_config['plugin'])
        db_name = cache_config['config']['db']
        if '%s' in db_name:
            db_name = db_name % self.data['name']
        config = {
            'endpoint': cache_config['config']['endpoint'],
            'metric': self.data['metric'],
            'db': db_name,
            'epoch': 'm',
            'tags': {
                'result': 'predict'
            }
        }
        self.cache_predict = cache_plugin.create(config)

    def cache_predict(self, timestamp, value):
        self.cache_predict.write([(timestamp, value)])

    @property
    def interval_minute(self):
        return self.data['interval_minute']

    def init_group(self):
        # chon 1 vm bat ky lam key de monitor
        self.enable_monitor_vm()

    def test(self, group_dict):
        return self.data['group_id'] == group_dict['group_id']

    @property
    def vms(self):
        return self.data['instances']

    @property
    def opsvm(self):
        return self.app.opsvm

    @property
    def log(self):
        return self.app.logger

    """ Task region
    """

    def enable_monitor_vm(self):
        vm = self.data['instances'][0]
        vm['is_monitoring'] = True
        self.groupservice.db_update_vm(vm)
        self.monitorcontroller = self.create_monitorcontroller(vm)

    def create_monitorcontroller(self, vm):
        group_config = {
            'endpoint': vm['endpoint'],
            # 'to_db': 'monitor_%s' % self.data['name'],
            'metric': self.data['metric'],
            'interval_minute': self.data['interval_minute'],
            'name': self.data['name']
        }
        return MonitorController(group_config, self.app)

    def create_scalecontroller(self):
        metric = self.data['metric']
        def_config = self.app.config['SCALE']['scale_controller'][metric]
        cf = copy.copy(def_config)
        cf['max_scale'] = self.app.config['SCALE']['max_scale']
        cf['warm_up_minutes'] = self.app.config['SCALE']['warm_up'] * self.interval_minute
        return self.app.scalefactory.create(self.data, cf)

    # return interval dau tien
    # return cache list neu data du de train
    def _run_init(self):
        interval = self.interval_minute
        result = self.monitorcontroller.init_data()
        interval = result['first_interval']
        total = result['total']

        # check time to wait to predict
        data_length = self.data['data_length']
        self.wait_cycle_training = data_length - total if data_length > total else 0

        if self.wait_cycle_training > 0:
            del result['cache']
            return interval, None
        else:
            # cache o day la pandas.core.series.Series
            return interval, result['cache']

            # values = self.monitorcontroller.get_data_series()

    def _run_train_data(self, data_cache):
        # data_cache la 1 mang pd.Series
        series = None
        if data_cache is not None:
            self.log.info('Group %s train with cache data' % self.logname)
            series = join_series(data_cache)
        metric = self.data['metric']
        forecast_cls = forecast_map[metric]
        config = copy.copy(self.data)
        forecast = forecast_cls(config, self.app)
        finish = []

        def train():
            try:
                self.log.debug('Group %s start train model' % self.logname)
                if series is None:
                    # get data
                    self.log.info(
                        'Group %s get data from influxdb to train' % self.logname)
                    accum = self.monitorcontroller.get_data_series()
                    if accum:
                        ita = [[it[1] for it in a] for a in accum]
                        del accum
                        data = join_series(ita)
                else:
                    data = series
                if data is None:
                    raise Exception("Can't get data from influxdb to train.")
                periods = forecast.train(data)
                self.log.info(
                    'Group %s data periods = %s' % (self.logname, periods))
                finish.append('success')
            except ServiceIOException as e:
                raise e
            except InstanceNotValid as e:
                raise e
            except Exception as e:
                finish.append(e.message)
            finally:
                self.log.debug('Group %s finish train with %s' %
                               (self.logname, finish))

        def get_forecast():
            if not finish:
                return
            elif finish[0] != 'success':
                raise Exception(finish)
            else:
                return forecast

        thread.start_new_thread(train, ())

        return get_forecast

    def _run(self):
        self.log.info('Group %s start' % self.logname)

        interval, cache = self._run_init()
        print(interval)
        if not cache and self.wait_cycle_training > 0:
            self.log.debug('Group %s wait %s cycle to train data' %
                           (self.logname, self.wait_cycle_training))
        state = 'wait'

        cache_list_when_train = None

        train_data_func = None
        self.wait_cycle_update = self.data['update_in_time']

        while self.is_running:
            need_update_model = False

            if state == 'wait':
                # truong hop dang doi model de train
                if self.wait_cycle_training > 0:
                    # neu lan dau tien khong du data thi xoa cache
                    del cache
                    cache = None
                    self.wait_cycle_training = self.wait_cycle_training - 1
                else:
                    # bao la co the train
                    state = 'run'
                    need_update_model = True
            else:
                # kiem tra dieu kien update model
                if self.wait_cycle_update > 0:
                    self.wait_cycle_update = self.wait_cycle_update - 1
                elif not train_data_func:
                    self.log.debug('Group %s time to update model.' %
                                   self.logname)
                    need_update_model = True

            if need_update_model and not train_data_func:
                # update forecast_model, cache co the null
                train_data_func = self._run_train_data(cache)
                # setup list nhan du lieu trong qua trinh train
                cache_list_when_train = []

            if train_data_func:
                try:
                    forecast = train_data_func()
                    if forecast is not None:
                        del self.forecast_model
                        self.forecast_model = forecast
                        train_data_func = None
                        self.wait_cycle_update = self.data['update_in_time']
                        # update cac diem luc dang doi
                        if cache_list_when_train:
                            for it in cache_list_when_train:
                                self.forecast_model.add_last_point(it)
                            cache_list_when_train = None
                except Exception as e:
                    train_data_func = None
                    self.log.debug('Group %s train data ERROR %s' %
                                   (self.logname, e.message))

            # self.thread_up_forcast_model =
            time.sleep(interval * 60)
            interval = self.interval_minute

            timestamp, value = None, None
            try:
                timestamp, value = self.monitorcontroller.get_last_one()
            except InstanceNotValid as e:
                # health check
                pass
            except Exception as e:
                self.log.error('Group %s error when get last point. Er %s' % (
                    self.logname, e.message))
            # luu lai value neu model dang train, trong truong hop thoi gian train
            # lon hon thoi gian interval_minute
            if cache_list_when_train is not None:
                cache_list_when_train.append(value)

            if timestamp is not None and value is not None:
                self.log.debug('Group %s get new value success' % self.logname)
            else:
                self.log.debug('Group %s get new value fail' % self.logname)

            if self.forecast_model:
                self.forecast_model.add_last_point(value)
                if value is not None:
                    pr = self.forecast_model.predict() or 0
                    self.log.debug('Group %s forecast value %s' %
                                   (self.logname, pr))
                    t = timestamp + self.interval_minute * \
                                    self.data['predict_length']
                    t = t * 1000000000 * 60
                    self.cache_predict.write([(t, pr)])

                    # scale
                    type_scale = self.scale_decide(value, pr)
                    if type_scale:
                        self.log.info('Group %s detect scale %s' % (self.logname, type_scale))

        self.log.info('Group %s stop' % self.logname)

    def scale_decide(self, value, pr):
        type_scale = self.scalecontroller.add_point(value, pr)

        result = self.scalecontroller.receive()
        if result and result['is_finish']:
            if result['state'] == 'success':
                if result['type'] == 'up':
                    # them vao danh sach
                    vm = result['vm']
                    vm['is_monitoring'] = False
                    self.groupservice.db_create_vm(vm)
                    # self.data['instances'].append(vm_dict)
                elif result['type'] == 'down':
                    vm = result['vm']
                    self.groupservice.db_drop_group(vm)
                self.log.info('Group % finish scale instance' % self.logname)
            else:
                self.log.info('Group % fail to scale instance' % self.logname)

        return type_scale

    def run(self):
        try:
            self._run()
        except ServiceIOException as e:
            raise e
        except InstanceNotValid as e:
            raise e

    """ Status region
    """

    def _get_collect_data_process(self):
        return {
            'name': 'collect',
            'data': {
                'interval': 'inverval',
                'accum': 'accum',
                'vmName': 'vm_name',
            }
        }

    def _get_training_data_process(self):
        return {
            'name': 'training',
            'data': {
                'interval': 'interval',
                'accum': 'accum',
                'vmName': 'vm_name',
                'lastTotalData': 'last_total_data'
            }
        }

    def _get_predict_data_process(self):
        return {
            'name': 'predict',
            'data': {
                'interval': 'interval',
                'accum': 'accum',
                'lastPredict': [],
                'vmName': 'vm_name'
            }
        }

    def _get_scale_process(self):
        return {
            'name': 'scale',
            'data': {
                'accumUp': 'accum_up',
                'accumDown': 'accum_down',
                'nVm': 'n_vm'
            }
        }

    def get_process_info_dict(self):
        # s = {
        #     'processes':[
        #         {
        #             'name': '',
        #             'data':{},
        #         }
        #     ]
        # }
        s = {
            'processes': [
                self._get_collect_data_process(),
                self._get_training_data_process(),
                self._get_predict_data_process(),
                self._get_scale_process()
            ]
        }
        return s

    """ VM regions
    """

    def scale_down(self):
        # tu chon ra 1 vm khong monitor de xoa
        vm = next((v for v in self.data['instances']
                   if not v['is_monitoring']), None)
        if not vm:
            self.log.error('Logic Error, khong tim thay vm de scale down')
        else:
            vmthread = self.opsvm.make_dropvm_thread(vm)

            self._scaling_threads.append(vmthread)
            thread.start_new_thread(self._scale_down_thread, (vmthread,))

    def _scale_down_thread(self, vmthread):
        vmthread.start()
        vmthread.stop()

        self._scaling_threads.remove(vmthread)

        if vmthread.status == 'success':
            self._last_scale_time = time.time()

            self.data['instances'].remove(vmthread.data)

            self.log.info('success scale down vm id=%s' %
                          vmthread.data['instance_id'])

        if vmthread.status == 'fail':
            self.log.error('fail to scale down vm id=%s' %
                           vmthread.data['instance_id'])

    def run_up(self):
        self.is_running = True
        self.start()

    def shutdown(self):
        self.is_running = False
