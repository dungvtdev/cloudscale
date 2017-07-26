import requests
import pandas as pd
import numpy as np
import json

endpoint = 'localhost:8086'
db_name = 'cache_test_group_v3'


def get_data(begin, end):
    url = 'http://{endpoint}/query'.format(endpoint=endpoint)

    # time_filter = 'time > now() - {begin}s AND time < now() - {end}s'
    time_filter = "time > '{begin}' AND time < '{end}'".format(begin=begin, end=end)
    q = 'SELECT "value" FROM "cpu_usage_total" WHERE {time_filter} GROUP BY result fill(null)'.format(
        time_filter=time_filter)

    payload = {
        'db': db_name,
        'q': q,
        'epoch': 's'
    }

    r = requests.get(url, params=payload)
    print(r.text)
    return r.text


def convert_to_dataframe(values):
    df = pd.DataFrame(values)
    array = np.asarray(df[1])
    time = pd.to_datetime(df[0] * 1000000000, format='%Y-%m-%d %H:%M:%S')
    convert = pd.DataFrame(array, index=time)
    return convert
    #return df

if __name__ == '__main__':
    begin = '2017-07-25 00:00:00'
    end = '2017-07-26 06:16:00'

    data = get_data(begin, end)
    data = json.loads(data)

    data = data['results'][0]['series']

    real = next((it for it in data if not it['tags']['result']), None)
    real = real['values']
    real_convert = convert_to_dataframe(real)
    # real_convert.to_csv('real.data.csv', index=False, header=False)
    # write file

    predict = next((it for it in data if it['tags']['result'] == 'predict'), None)
    predict = predict['values']
    predict_convert = convert_to_dataframe(predict)
    # predict_convert.to_csv('predict.data.csv', index=False, header=False)

    scale_up = next((it for it in data if it['tags']['result'] == 'scale_up'), None)
    scale_up = scale_up['values']
    scale_up_convert = convert_to_dataframe(scale_up)
    scale_up_convert.index = scale_up_convert.index.shift(-4, freq='m')

    scale_down = next((it for it in data if it['tags']['result'] == 'scale_down'), None)
    scale_down = scale_down['values']
    scale_down_convert = convert_to_dataframe(scale_down)
    scale_down_convert.index = scale_down_convert.index.shift(-4, freq='m')
    
    th = pd.concat([real_convert, predict_convert, scale_up_convert, scale_down_convert], axis=1)
    th.to_csv('data.result.csv', header=False)

