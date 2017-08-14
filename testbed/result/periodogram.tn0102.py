import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
from pandas.lib import Timestamp
from scipy import signal
from segmentation import segment, fit
from matplotlib import pyplot as plt

def period_detect(series, fs=1440, threshold=0.2, periodogram_candiate=8, max_error=0.005, segment_method="topdownsegment"):
    # dau vao df theo dinh dang cua twitter
    # fs: tan so lay mau (sample per day)
    if not isinstance(series, pd.Series):
        raise ValueError(("data must be a single data frame, "
                          "list, or vector that holds numeric values."))

    n = len(series)
    print(n)

    # mien tan so
    data_value_trans = series - series.median()
    f, Pxx_den = signal.periodogram(
        data_value_trans, fs, window=signal.get_window('hamming', n))
    # print(len(f))
    # print(f)
    t = 0.02 * np.max(Pxx_den)
    i_draw = [i for i in range(1, Pxx_den.size) if Pxx_den[i]>=t and f[i] < (n-1)/fs]
    p_draw = [f[i] for i in i_draw]
    y_draw = [Pxx_den[i] for i in i_draw]
    plt.semilogy(p_draw, y_draw)
    plt.xlabel('Days')
    plt.ylabel('Power')
    # plt.semilogy(f, Pxx_den)
    # plt.xlabel('frequency [Hz]')
    # plt.ylabel('PSD [V**2/Hz]')
    # plt.show()

    # chon nguong 40 %
    threshold = threshold * np.max(Pxx_den)
    index_period_candidate = [i for i in range(1, Pxx_den.size - 1) if (
        (Pxx_den[i] > threshold) and (Pxx_den[i] > Pxx_den[i + 1]) and (Pxx_den[i] > Pxx_den[i - 1]))]
    period_candidate = [f[i]
                        for i in index_period_candidate if (f[i] < (n - 1) / fs)]
    period_candidate_pxx = [Pxx_den[i]
                            for i in index_period_candidate if (f[i] < (n - 1) / fs)]

    plt.scatter(period_candidate, period_candidate_pxx)
    for a,b in zip(period_candidate, period_candidate_pxx):
        plt.text(a, b, str('  p=%0.2f' % a))
    # plt.show()
    # plt.semilogy(period_candidate, period_candidate_pxx)
    # # plt.semilogy(f, Pxx_den)
    # plt.xlabel('frequency [Hz]')
    # plt.ylabel('PSD [V**2/Hz]')
    plt.show()

    t = {
        'period': period_candidate,
        'magnitude': period_candidate_pxx
    }
    period_candidate_point = pd.DataFrame(t)
    # chi lay 1 so luong candidate nhat dinh
    # ham nlargest tra lai thu tu theo manitude gian dan
    # do do ung vien dau tien la ung vin co Pxx lon nhat
    period_candidate_point = period_candidate_point.nlargest(
        periodogram_candiate, 'magnitude')

    lag = range(0, n - 1)
    autocorr = [np.correlate(series, np.roll(series, -i))
                [0] / series.size for i in lag]
    
    days = [l*1.0/fs for l in lag]
    ids = [next(i for i in range(1,len(days)-1) if p > days[i-1] and p < days[i+1]) for p in period_candidate]
    ps = [days[i] for i in ids]
    psy = [autocorr[i] for i in ids]
    print(period_candidate)
    # print(ps)
    # print(psy)
    plt.scatter(ps, psy)
    plt.plot(days, autocorr)
    plt.xlabel('Days')
    plt.ylabel('ACF')
    plt.show()
    # ACF_candidate = [autocorr[int(i*fs)] for i in period_candidate_point['period']]

    final_all_period = []
    for period_temp in period_candidate_point['period']:
        startpoint = (int)(period_temp * fs)
        temp = autocorr[startpoint]

        begin_frame = np.max([(startpoint - fs), 0])
        end_frame = np.min([startpoint + fs, len(autocorr)])

        max = np.max(autocorr[begin_frame:end_frame])
        min = np.min(autocorr[begin_frame:end_frame])
        tb = (max + min) / 2
        if(max - min > 0):
            autocorr_normalize = (np.array(autocorr) - tb) / (max - min)
        else:
            return final_all_period
        segments = []
        try:
            if(segment_method == "slidingwindowsegment"):
                segments = segment.slidingwindowsegment(
                    autocorr_normalize[begin_frame:end_frame], fit.regression, fit.sumsquared_error, max_error)
            if (segment_method == "topdownsegment"):
                segments = segment.topdownsegment(autocorr_normalize[begin_frame:end_frame], fit.regression,
                                                  fit.sumsquared_error, max_error)
            if (segment_method == "bottomupsegment"):
                segments = segment.bottomupsegment(autocorr_normalize[begin_frame:end_frame], fit.regression,
                                                   fit.sumsquared_error, max_error)

        except:
            pass

        if len(segments) < 3:
            continue
        # check xem co la hill ko
        # diem start point la 200 (trong khoang moi 401 diem dang xet)
        # tim doan seg cua diem nay
        # seg_index = 0
        for i in range(0, len(segments)):
            if startpoint - begin_frame < segments[i][2]:
                seg_index = i
                break
        if ((seg_index < 2) or (seg_index > len(segments) - 2)):
            continue
        dh_trai = (segments[seg_index][3] - segments[seg_index][1]) - (
            segments[seg_index - 1][3] - segments[seg_index - 1][1])
        dh_phai = (segments[seg_index + 1][3] - segments[seg_index + 1][1]) - (
            segments[seg_index][3] - segments[seg_index][1])

        if ((dh_phai < 0) and (dh_trai < 0)):  # diem nam tren hill tien hanh tim closest peak
            while (segments[seg_index][3] > segments[seg_index][1]):
                # di tu trai sang phai
                # khi nao ma dao ham con duong thi di tu trai sang phai
                seg_index = seg_index + 1
                if (seg_index > len(segments) - 2):
                    break
            while (segments[seg_index][3] < segments[seg_index][1]):
                # khi nao dao ham con am thi di tu phai sang trai
                seg_index = seg_index - 1
                if ((seg_index < 2)):
                    break
            if ((seg_index >= 2) and (seg_index <= len(segments) - 2)):
                final_period = segments[seg_index][2]
                final_all_period.append(final_period + begin_frame)
    return [x * 1.0 / fs for x in final_all_period]

filename = 'data.result.tn.03.csv'

data = pd.read_csv(filename, header=None)

# time = pd.to_datetime(data[0], format='%Y-%m-%d %H:%M:%S')

# real = pd.Series(np.asarray(data[1]), index=time)
real = pd.Series(np.asarray(data[1]))
real = real.interpolate()
# real = real[:1600]
# real = real[:5140]
real = real[300:len(real)-100]

for i in range(875, 908):
    real[i]=0.45

for i in range(1825, 1875):
    real[i]=0.5

fs = 720
threshold=0.15

# data_value_trans = real - real.median()
# f, Pxx_den = signal.periodogram(
#     data_value_trans, fs, window=signal.get_window('hamming', len(real)))

# for i in range(len(f)-1):
#     if f[i] <=0.3333 and f[i+1]>=0.3333:
#         print(Pxx_den[i]/np.max(Pxx_den))
#         break

plt.plot(real.index, real)
plt.xlabel('Point')
plt.ylabel('% CPU / 100')

plt.show()

# for i in range(3):
#     # dr = real[:5140+i*240]
#     dr = real
#     ps = period_detect(dr, fs=fs, threshold=threshold, max_error=0.005)
#     print('period %s'  % ps)

# i=17
# real = real[:len(real)-i]
# ps = period_detect(real,fs=fs, threshold=threshold, max_error=0.005)
# print('%s period %s'  % (i, ps))

# save = []
# for i in range(200):
#     d = real[:len(real)-i]
#     ps = period_detect(d,fs=fs, threshold=threshold, max_error=0.005)
#     print('%s period %s'  % (i, ps))

#     if ps and ps[0] <= 1.5:
#         save.append((i, ps))
#         break

# print(save)

ps = period_detect(real,fs=fs, threshold=threshold, max_error=0.005)
print('period %s'  % ps)
