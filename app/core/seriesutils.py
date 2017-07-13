import pandas as pd
import numpy as np


def minutevaluepair_to_pdseries(timevalues):
    df = timevalues if isinstance(timevalues, pd.DataFrame) \
        else pd.DataFrame(timevalues)
    convert = 1000000000 * 60   # tinh theo minute
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