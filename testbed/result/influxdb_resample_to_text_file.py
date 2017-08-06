import requests
import pandas as pd
import numpy as np
import json

endpoint = '192.168.122.124:8086'
db_name = 'cadvisor'


def get_data(begin, end):
    url = 'http://{endpoint}/query'.format(endpoint=endpoint)

    # time_filter = 'time > now() - {begin}s AND time < now() - {end}s'
    time_filter = "time > '{begin}' AND time < '{end}'".format(begin=begin, end=end)
    q = 'SELECT derivative("value", 1s)/1000000000 FROM cpu_usage_total WHERE {time_filter} GROUP BY "container_name" fill(null)'.format(time_filter=time_filter)

    payload = {
        'db': db_name,
        'q': q,
        'epoch': 's'
    }

    r = requests.get(url, params=payload)
    return r.text


def convert_to_dataframe(values):
    df = pd.DataFrame(values)
    array = np.asarray(df[1])
    time = pd.to_datetime(df[0] * 1000000000, format='%Y-%m-%d %H:%M:%S')
    convert = pd.DataFrame(array, index=time)
    return convert
    #return df

def downsample(data, minute):
    return data.resample('%sT' % minute).mean()

if __name__ == '__main__':
    begin = '2017-08-06 00:00:00'
    end = '2017-08-06 22:01:00'

    data = get_data(begin, end)
    data = json.loads(data)

    data = data['results'][0]['series']

    real = next((it for it in data if it['tags']['container_name']=='/'), None)
    real = real['values']
    real_convert = convert_to_dataframe(real)
    real_resample = downsample(real_convert, 2)
    
    # th = pd.concat([real_convert, predict_convert, scale_up_convert, scale_down_convert], axis=1)
    real_resample.to_csv('data.test.cpu.csv', header=False)

