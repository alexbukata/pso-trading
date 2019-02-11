import datetime as dtm

from iexfinance.stocks import get_historical_data

from src.indicators import onbalance_volume, moving_average, relative_strength_index, merge


def prepare_data(share, start, end):
    start = start - dtm.timedelta(days=14)

    data = get_historical_data(share, start, end)
    market_data = get_historical_data('SPY', start, end)

    obv = onbalance_volume(data)
    moving_averages_21 = moving_average(data, window_size=21)
    moving_averages_14 = moving_average(data, window_size=14)
    moving_averages_7 = moving_average(data, window_size=7)
    moving_averages_3 = moving_average(data, window_size=3)
    rsi_21 = relative_strength_index(data, window_size=21)
    rsi_14 = relative_strength_index(data)
    rsi_7 = relative_strength_index(data, window_size=7)
    rsi_3 = relative_strength_index(data, window_size=3)

    # build_plots(data, obv, moving_averages_7, moving_averages_14)

    obv = dict(obv)
    moving_averages_21 = dict(moving_averages_21)
    moving_averages_14 = dict(moving_averages_14)
    moving_averages_7 = dict(moving_averages_7)
    moving_averages_3 = dict(moving_averages_3)
    rsi_21 = dict(rsi_21)
    rsi_14 = dict(rsi_14)
    rsi_7 = dict(rsi_7)
    rsi_3 = dict(rsi_3)

    return merge(data, obv, moving_averages_21, moving_averages_14, moving_averages_7, moving_averages_3, rsi_21,
                 rsi_14, rsi_7, rsi_3)
