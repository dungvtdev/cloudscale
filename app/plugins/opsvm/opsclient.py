from novaclient.client import Client
from novaclient import exceptions

from keystoneauth1.identity import v3
from keystoneauth1 import session

import time


class OSClient(object):
    _instance = None

    def __init__(self, config):
        super(OSClient, self).__init__()
        self._setup(config)

    @classmethod
    def default(cls):
        if OSClient._instance is None:
            OSClient._instance = OSClient()
        return OSClient._instance

    def _setup(self, cf):
        auth = v3.Password(auth_url=cf['auth_url'],
                           user_domain_name=cf['user_domain_name'],
                           username=cf['username'],
                           password=cf['password'],
                           project_domain_name=cf['project_domain_name'],
                           project_name=cf['project_name'])
        sess = session.Session(auth=auth)
        self.client = Client(cf['nova_version'], session=sess)

    def _show_server(self, instance_id):
        server = self.client.servers.get(instance_id)
        return server

    def _list_servers(self):
        servers = self.client.servers.list()
        return servers

    def _list_ip(self, instance_id):
        return dict(self.client.servers.ips(instance_id))

    def _list_nic(self, instance_id):
        interfaces = self.client.servers.interface_list(instance_id)
        return interfaces

    def _show(self, instance_id):
        server = self.client.servers.get(
            instance_id
        )
        return server

    def _reboot(self, instance_id):
        self.client.servers.reboot(instance_id)

    def create(self, image_id, flavor_id,
               network_id, name=None, user_data=None, **kargs):
        server = self.client.servers.create(
            name,
            image_id,
            flavor_id,
            nics=[{'net-id': network_id}, ],
            userdata=user_data
        )
        return server

    def _get_new_floating_ip(self, pool_name):
        ips = self.client.floating_ips.list()
        ip = next((ip for ip in ips
                   if ip.pool == pool_name and ip._loaded and ip.instance_id is None), None)
        if ip is None:
            ip = self.client.floating_ips.create(pool_name)
        return ip

    def _associate_public_ip(self, instance_id, public_ip_id, private_ip=None):
        """Associate a external IP"""
        floating_ip = self.client.floating_ips.get(public_ip_id)
        floating_ip = floating_ip.to_dict()
        address = floating_ip.get('ip')

        self.client.servers.add_floating_ip(instance_id, address, private_ip)

        return True

    def reboot_instance(self, instance_id, time_out, check_interval):
        self._reboot(instance_id)
        success = self._check_instance_booting(instance_id, time_out, check_interval)
        return success

    def _check_instance_booting(self, instance_id, timeout, check_interval):
        while timeout >= 0:
            time.sleep(check_interval)
            timeout = timeout - check_interval
            s_status = self._show(instance_id)
            # print(vars(s_status))
            if s_status.status == 'ACTIVE':
                return True
            elif s_status.status == 'ERROR':
                return False
        return False

    def create_new_instance(self, name, image_id, flavor_id, net_selfservice_id,
                            provider_name, user_data=None, time_out=None, check_interval=None, try_again=None):
        try_again = try_again or 0
        try:
            count = try_again + 1
            while count > 0:
                count = count - 1
                # create new instance
                server = self.create(image_id=image_id,
                                     flavor_id=flavor_id,
                                     network_id=net_selfservice_id,
                                     name=name,
                                     user_data=user_data)
                timeout = time_out or 20
                success = self._check_instance_booting(server.id, timeout, check_interval)

                if success:
                    break
                else:
                    self.delete(server.id)

            if not success:
                raise Exception('Create vm fails')

            # check floating ip available
            ip = self._get_new_floating_ip(provider_name)
            self._associate_public_ip(server.id, ip.id)
            return {
                'instance_id': server.id,
                'ip': ip.ip,
            }
        except Exception as e:
            raise e

    def delete(self, instance_id):
        self.client.servers.delete(instance_id)
        return True

    def get_instance_info(self, instance_id):
        # status = ['BUILD', 'SHUTOFF', 'ACTIVE', ]
        try:
            s_status = self._show(instance_id)
            ip = None
            for k, v in s_status.addresses.items():
                ip = next(
                    (it['addr'] for it in v if it['OS-EXT-IPS:type'] == 'floating'), None)
                if ip is not None:
                    break
            return {
                'status': s_status.status,
                'ip': ip
            }
        except Exception as e:
            print(e)
