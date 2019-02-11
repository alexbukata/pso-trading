import datetime as dtm
from operator import itemgetter
from random import shuffle

import matplotlib.dates as plt_dates
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from mpl_finance import candlestick_ohlc

sns.set()


def relative_strength_index(data, window_size=14):
    result = []
    entries = list(data.items())

    windowed_entries = entries[:window_size]
    entries_diff = list(map(lambda x: x[1]['close'] - x[1]['open'], windowed_entries))
    uptrend_days = list(filter(lambda x: x > 0, entries_diff))
    downtrend_days = list(filter(lambda x: x < 0, entries_diff))
    avg_uptrend = np.sum(uptrend_days) / window_size
    avg_downtrend = -np.sum(downtrend_days) / window_size
    rsi = 100 - (100 / (1 + avg_uptrend / avg_downtrend))
    result.append((entries[window_size - 1][0], rsi))

    for i in range(window_size, len(entries)):
        current_diff = entries[i][1]['close'] - entries[i][1]['open']
        gain, loss = (current_diff, 0) if current_diff > 0 else (0, -current_diff)
        avg_uptrend = (avg_uptrend * (window_size - 1) + gain) / window_size
        avg_downtrend = (avg_downtrend * (window_size - 1) + loss) / window_size
        rsi = 100 - (100 / (1 + avg_uptrend / avg_downtrend))
        result.append((entries[i][0], rsi))
    return result


def moving_average(data, window_size=14):
    result = []
    entries = list(data.items())
    windowed_entries = entries[:window_size]
    windowed_entries = list(map(lambda entry: entry[1]['close'], windowed_entries))
    last_mean = np.mean(windowed_entries)
    first_windowed_entry = windowed_entries[0]
    result.append((entries[window_size - 1][0], last_mean))

    for i in range(window_size, len(entries)):
        # simplified: (last_mean * 20 - first_windowed_entry + last_close)/20
        last_mean = last_mean + (entries[i][1]['close'] - first_windowed_entry) / window_size
        first_windowed_entry = entries[i - window_size + 1][1]['close']
        result.append((entries[i][0], last_mean))
    return result


def onbalance_volume(data, normalize=True):
    result = []
    entries = list(data.items())
    if entries[1][1]['close'] > entries[0][1]['close']:
        obv = entries[1][1]['volume']
    elif entries[1][1]['close'] < entries[0][1]['close']:
        obv = -entries[1][1]['volume']
    else:
        obv = 0
    result.append((entries[1][0], obv))
    for i in range(2, len(entries)):
        # simplified: (last_mean * 20 - first_windowed_entry + last_close)/20
        if entries[i][1]['close'] > entries[i - 1][1]['close']:
            obv += entries[i][1]['volume']
        elif entries[i][1]['close'] < entries[i - 1][1]['close']:
            obv += -entries[i][1]['volume']
        else:
            obv += 0
        result.append((entries[i][0], obv))
    if normalize:
        obv_max = max(result, key=itemgetter(1))[1]
        # obv_max = 9
        first_number = 9
        # obv_sum = abs(sum(map(itemgetter(1), result)))
        result = list(map(lambda x: (x[0], 10 * x[1] / obv_max), result))
    return result


def merge(data, *indicators):
    x = []
    y = []
    items = list(data.items())
    for i, key_value in enumerate(items):
        key, value = key_value
        if len(items) - 1 == i or \
                any(map(lambda indic: key not in indic, indicators)):
            continue

        entry = list(map(itemgetter(key), indicators))
        entry.append(items[i][1]['open'] - items[i + 1][1]['open'])
        # entry.append(items[i][1]['high'] - items[i][1]['low'])
        # entry = [moving_averages_7[key], moving_averages_14[key], obv[key], rsis[key], items[i + 1][1]['open']]
        x.append(entry)
        y.append(int(items[i + 1][1]['close'] > items[i + 1][1]['open']))
    zipped_xy = list(zip(x, y))
    # shuffle(zipped_xy)
    x, y = zip(*zipped_xy)
    return np.array(x), np.array(y)


def build_plots(data, obv, moving_averages_7, moving_averages_14):
    i = 0
    ohlc = []
    averages14_chart_x = []
    averages14_chart_y = []
    averages7_chart_x = []
    averages7_chart_y = []
    obv_x = []
    obv_y = []
    for date, entry in data.items():
        candle_date = dtm.datetime.strptime(date, '%Y-%m-%d')
        candle_date_num = plt_dates.date2num(candle_date)
        candle_data = candle_date_num, entry['open'], entry['high'], entry['low'], entry['close'], entry['volume']
        ohlc.append(candle_data)
        if i < len(obv):
            obv_y.append(obv[i][1])
            obv_date = dtm.datetime.strptime(obv[i][0], '%Y-%m-%d')
            obv_x.append(plt_dates.date2num(obv_date))
        if i < len(moving_averages_14):
            averages14_chart_y.append(moving_averages_14[i][1])
            mav_date = dtm.datetime.strptime(moving_averages_14[i][0], '%Y-%m-%d')
            averages14_chart_x.append(plt_dates.date2num(mav_date))
        if i < len(moving_averages_7):
            averages7_chart_y.append(moving_averages_7[i][1])
            mav_date = dtm.datetime.strptime(moving_averages_7[i][0], '%Y-%m-%d')
            averages7_chart_x.append(plt_dates.date2num(mav_date))
        i += 1

    subplt = plt.subplot(2, 1, 1)
    candlestick_ohlc(subplt, ohlc, width=0.4, colorup='#77d879', colordown='#db3f3f')
    plt.plot(averages14_chart_x, averages14_chart_y, '-')
    plt.plot(averages7_chart_x, averages7_chart_y, '-')

    plt.subplot(2, 1, 2)
    plt.plot(obv_x, obv_y, '-')

    plt.show()
