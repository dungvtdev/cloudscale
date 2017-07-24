import requests
import json

endpoint = '192.168.122.124'
dbname = 'cadvisor'

delta_secs = 5*60*60

chunks = [('2017-07-23 10:30:00', '2017-07-23 12:40:00')]

for chunk in chunks:
    url = 'http://%s:8086/query' % endpoint
    query = "select * from cpu_usage_total where time > '{begin}' and time < '{end}'".format(begin=chunk[0], end=chunk[1])
    params = {
        'epoch': 's',
        'db': dbname,
        'q': query
    }
    r = requests.get(url, params)
    values = json.loads(r.text)['results'][0]['series'][0]['values']

    # send
    line = "cpu_usage_total,container_name={cn},machine={mc} value={vl}i {time}"
    d_str = '\n'.join(line.format(cn=val[1], mc=val[2], vl=int(val[3]), time=(val[0]+delta_secs)*1000000000) for val in values)

    print(d_str)
    url = 'http://%s:8086/write?db=%s' % (endpoint, dbname)
    r = requests.post(url, data=d_str)
    print(r.text)
