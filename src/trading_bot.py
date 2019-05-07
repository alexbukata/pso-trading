def simulate_allin_hold(decision_func, stocks, initial_cash=500_000, multipl=1):
    cash = initial_cash
    capacity = {}
    for index, row in stocks.iterrows():
        decision = decision_func(row)
        if row['stock_name'] not in capacity:
            capacity[row['stock_name']] = 0
        curr_capacity = capacity[row['stock_name']]
        if decision == 'buy':
            if curr_capacity == 0 and cash > multipl * row['open']:
                curr_capacity += multipl
                cash -= multipl * row['open']
        elif decision == 'sell':
            if curr_capacity > 0:
                cash += curr_capacity * row['open']
                curr_capacity = 0
        capacity[row['stock_name']] = curr_capacity
        print(f'cash={cash}, capacity={capacity}')
    for stock_name, curr_capacity in capacity.items():
        last_trading_day = stocks[stocks['stock_name'] == stock_name].tail(1)
        cash += curr_capacity * float(last_trading_day['close'])
    print(cash)


def simulate_trading(decision_func, stocks, initial_cash=500_000, multipl=1, interest_percent=0.3):
    cash = initial_cash
    min_cash = cash
    max_cash = cash
    for index, row in stocks.iterrows():
        decision = decision_func(row)
        difference = multipl * (row['close'] - row['open'])
        if decision == 'buy':
            if cash > multipl * row['open']:
                open = row['open']
                interest = multipl * row['open'] * (interest_percent / 100.0)
                cash += multipl * (row['close'] - row['open']) - interest
                print(f'buy: open: {open}, cash={cash}, diff={difference}, interest={interest}')
        elif decision == 'sell':
            open = row['open']
            interest = multipl * row['close'] * (interest_percent / 100.0)
            cash += multipl * (row['open'] - row['close']) - interest
            print(f'sell: open: {open}, cash={cash},  diff={difference}, interest={interest}')
        if cash > max_cash:
            max_cash = cash
        if cash < min_cash:
            min_cash = cash
        if cash < 0:
            print("bankrot!")
            break
    return cash, min_cash, max_cash


if __name__ == '__main__':
    stocks = pd.read_csv('..\\stocks.csv')
    stocks['date'] = pd.to_datetime(stocks['date'], format="%Y-%m-%d")
    simulate_trading(lambda x: 'sell', stocks, initial_cash=300, multipl=200)
