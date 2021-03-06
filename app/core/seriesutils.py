import pandas as pd
import numpy as np


# Ham nay doi timestamp index sang number index nen rat quan trong
# la cho duy nhat trong code lam viec nay
#
def join_series(series_list):
    if not series_list:
        return None

    s = pd.Series([])
    for si in series_list:
        s = s.append(si, ignore_index=True)
    return s


def normalize(data, dmin=None, dmax=None):
    if isinstance(data, list):
        data = pd.DataFrame(data)[0]
    elif isinstance(data, np.ndarray):
        data = pd.DataFrame(data)[0]

    dmin = data.min() if dmin is None else dmin
    dmax = data.max() if dmax is None else dmax
    return (data - dmin) / (dmax - dmin), dmin, dmax


def minutevaluepair_to_pdseries(timevalues):
    df = timevalues if isinstance(timevalues, pd.DataFrame) \
        else pd.DataFrame(timevalues)
    convert = 1000000000 * 60  # tinh theo minute
    df = df.set_index(pd.to_datetime(df[0] * convert))[1]
    return df


def resample(pdtimeseries, sampleMinute):
    sample = '%sT' % sampleMinute
    df = pdtimeseries.resample(sample).mean()
    return df


def get_newestseries(pdtimeseries, max_fault_point=0):
    # check series khong bi gian doan
    count = 0
    from_idx = 0
    for i in range(len(pdtimeseries))[::-1]:
        if np.isnan(pdtimeseries[i]):
            count = count + 1
        else:
            from_idx = i
            count = 0
        if count > max_fault_point:
            # lay doan tu from_idx
            s = pdtimeseries[from_idx:]
            # interpolate
            s = s.interpolate()
            return s
    return pdtimeseries.interpolate()


def clamp01(data):
    data[(data > 1) | (data < 0)] = np.nan
    data = data.interpolate()
    i = 0
    while np.isnan(data[i]):
        data[i] = 0
        i = i + 1
    return data


def force_positive(data):
    data[(data < 0)] = np.nan
    data = data.interpolate()
    i = 0
    while np.isnan(data[i]):
        data[i] = 0
        i = i + 1
    return data


def force_exceed_zero(data):
    if isinstance(data, list):
        data = pd.Series(data)
    data[(data <= 0)] = np.nan
    data = data.interpolate()
    i = 0
    while np.isnan(data[i]):
        data[i] = 0
        i = i + 1
    return data


def interpolate_to_pandas_series(list_data):
    s = pd.Series(list_data)
    s = s.interpolate()
    return s
