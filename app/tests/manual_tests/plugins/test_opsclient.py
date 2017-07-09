import pprint
import setup_test
from plugins.opsvm.opsclient import OSClient

provider_id = '14e16981-0816-4ed7-a612-1388ff974ada'
selfservice_id = 'bb87469e-183e-4d89-a287-5397d6bac5e4'
image_id = 'd0111621-ab84-47c3-9f4c-ebae9a8e8c91'
flavor_id = 'b6f1a774-a56c-47ec-b43c-ed67babe5da7'
floating_ip = '1164fad8-26e8-48de-bc4f-77f6ac19766a'
instance_id = 'a55acfb5-6544-481b-870c-a69b98bdbfb2'

config = {
    'auth_url': 'http://controller:5000/v3',
    'user_domain_name': 'default',
    'username': 'admin',
    'password': '123',
    'project_domain_name': 'default',
    'project_name': 'admin',
    'nova_version': '2.1'
}

if __name__ == '__main__':
    client = OSClient(config)

    servers = client._list_servers()
    for s in servers:
        info = client.get_instance_info(s.id)
        print(info)

    # server = client._show('2fb873c6-ea1c-43c8-aede-382e912550fa')
    # dumps_object(server)
    server = client.create(image_id=image_id,
                           flavor_id=flavor_id,
                           network_id=selfservice_id,
                           name='testxxx')
    pprint.pprint(vars(server))

    # success = client.associate_public_ip(instance_id, floating_ip)
    # print(success)

    # ip = client.get_new_floating_ip('provider')
    # dumps_object(ip)

    # ips = client.client.floating_ips.list()
    # for ip in ips:
    #     dumps_object(ip)

    # server = client.create_new_instance(name='vm111', image_id=image_id,
    #                                     flavor_id=flavor_id,
    #                                     net_selfservice_id=selfservice_id,
    #                                     provider_name='provider')
    # print(server)

    # time.sleep(2)
    # client.delete(server['instance_id'])
