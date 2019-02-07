from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from iexfinance.stocks import get_historical_data
from sklearn import svm


def get_stock_return(symbols, start, end):
    data = get_historical_data(symbols, start, end)
    keys = []
    values = []
    for key, value in data.items():
        keys += [[0 if value['close'] > value['open'] else 1, value['high'], value['low']]]
        values += [value['close']]
    return keys, values


if __name__ == '__main__':
    aapl = 'AAPL'
    start = datetime(2017, 1, 1)
    end = datetime(2019, 1, 1)
    data = get_stock_return(aapl, start, end)
    # data = get_historical_data(aapl, start, end)
    # data = dict(map(lambda keyval: (keyval[0], keyval[1]['close']), data.items()))
    # dates = data.keys()
    # returns = data.values()
    # data = [(i, a_return) for i, a_return in enumerate(returns)]

    # split to test and train
    x, y = data
    x_train = np.array(x[:len(x) // 2])
    y_train = np.array(y[:len(y) // 2])

    x_test = np.array(x[len(x) // 2:])
    y_test = np.array(y[len(y) // 2:])

    # classifier
    svc = svm.LinearSVR()
    svc.fit(x_train, y_train)

    y_test_predicted = list(map(lambda x: svc.predict([x]), x_test))

    # plot
    plt.plot(y_test)
    plt.plot(y_test_predicted)
    plt.show()
    print()
