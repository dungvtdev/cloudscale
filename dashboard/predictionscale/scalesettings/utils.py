from openstack_dashboard.dashboards.predictionscale.backend \
    import client


def drop_group(request, group_id):
    client(request).drop_group(group_id)


def create_group(request, group):
    return client(request).add_group(group)

def update_group(request, group, id):
    return client(request).update_group(group, id)

def enable_group(request, id):
    return client(request).enable_group(id)


def disable_group(request, id):
    return client(request).disable_group(id)

    
def get_data_length(request, id, *args):
    return client(request).get_data_length(id, *args)


def run_group(request, id, params):
    return client(request).run_group(id, params)


def poll_process_data(request, id):
    return client(request).poll_process_data(id)

def get_last_predict(request, id):
    return client(request).get_last_predict(id)

def get_report_data(request, instance_id):
    return client(request).get_report_data(instance_id)
