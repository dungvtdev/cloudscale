from openstack_dashboard import api
from horizon import exceptions
from django.utils.translation import ugettext_lazy as _


def get_instances_ip(request, instance_ids, ip_type='floating'):
    ip_type = ip_type or 'fixed'
    try:
        tmp_instances, _more = api.nova.server_list(
            request,
            all_tenants=True)
    except Exception:
        self._more = False
        exceptions.handle(request,
                          _('Unable to retrieve instance list.'))
        return

    instances = []
    for inst in tmp_instances:
        if inst.id in instance_ids:
            instances.append(inst)

    try:
        api.network.servers_update_addresses(request, instances,
                                             all_tenants=True)
    except Exception:
        exceptions.handle(
            request,
            message=_('Unable to retrieve IP addresses from Neutron.'),
            ignore=True)
    # print('**************** instance ip ***********************')
    # print(instances)
    # print('*****************************************')
    ips = {}
    for inst in instances:
        for k, addresses in inst.addresses.items():
            ip = None
            for address in addresses:
                if ('OS-EXT-IPS:type' in address and
                            address['OS-EXT-IPS:type'] == "floating"):
                    ip = address['addr']
                    break
            if ip is not None:
                ips[inst.id] = ip
                break

    return ips
