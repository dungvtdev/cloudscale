import requests


def check_ops(app, group_data):
    print('************ Check OPS *********************')
    # thu tao va huy may ao
    print('Check OPS scale up')
    up_thread = app.opsvm.make_createvm_thread(group_data)
    up_thread.start()
    up_thread.join()
    create_success = up_thread.state == 'success'
    print('OPS scale up is ok %s' % create_success)
    if create_success:
        print('Check OPS scale down')
        vm = up_thread.vm
        down_thread = app.opsvm.make_dropvm_thread(vm)
        down_thread.start()
        down_thread.join()
        down_success = down_thread.state
        print('OPS scale down %s' % ('OK' if down_success else 'Fail'))


def check_vm(app, group_data):
    print('************ Check VM *********************')

    insts = group_data['instances']
    port = app.config['DEFAULT_PARAMS']['scale']['app_port']

    for inst in insts:
        # check app running
        r = requests.get('http://%s:%s/ping' % (inst['endpoint'], port))
        success = r.status_code == 200 and 'hostname' in r.text
        print('Check vm app test %s' % success)
        # check influxdb
        r = requests.get('http://%s:8086/ping' % inst['endpoint'])
        success = r.status_code == 201
        print('Check influxdb running %s' % success)


def check_haproxy(app):
    print('************ Check haproxy *********************')

    haproxy = app.haproxy
    haproxy.add_server('1.1.1.1', 8000, 8808)

    haconfig = app.config['LOADBALANCER']['config_path']
    with open(haconfig, 'r') as f:
        s = f.read()
        success = '1.1.1.1' in s
    print('Check proxy %s' % success)
    haproxy.remove_server('1.1.1.1', 8000, 8808)


def check_cache(app, group_data):
    print('************ Check cache *********************')

    # check
    cache_endpoint = app.config['GROUPCACHE']['cache_plugin']['config']['endpoint']
    r = requests.get('http://%s:8086/query?q=SHOW DATABASES' % cache_endpoint)
    success = r.status_code == 200

    if success:
        db_name = app.config['GROUPCACHE']['cache_plugin']['config']['db']
        cache_name = db_name % group_data['name']
        success = cache_name not in r.text

    print('Check cache success is %s' % success)


def check_all(app, group_data):
    check_vm(app, group_data)
    check_haproxy(app)
    check_cache(app, group_data)
    check_ops(app, group_data)
