import datetime as dtm
import logging as log
import time

import pandas as pd
import requests

_intrinio_key_sand = 'OjYxNzRmMDQyZDM1NTVkOGEzMDAwYjA4MTI1YWY0ZThj'
_intrinio_key_prod = 'OjM1MTMyNDljOTI4ODY4N2YxMGMzMmQ2OThiNGI5YzZj'
_current_key = _intrinio_key_sand


def get_stocks_data(stock_names, datefrom, dateto):
    result = pd.DataFrame()
    stock_candidate_names = list(stock_names)
    while len(stock_candidate_names) > 0:
        stock_name = stock_candidate_names.pop()
        try:
            current_stocks = _get_stock_data(stock_name, datefrom, dateto)
            result = pd.concat([result, current_stocks])
        except Exception as e:
            print("retry on {}".format(stock_name))
            print(e)
            stock_candidate_names.append(stock_name)
        time.sleep(3)

    return result


def _get_stock_data(stock_name, datefrom, dateto):
    print(stock_name)
    log.info("[{}] request stock prices".format(stock_name))
    stock_data = _request_stock_prices_as_pd(stock_name, datefrom, dateto)
    log.info("[{}] request stock technicals".format(stock_name))
    current_stock_technicals = _request_stock_technicals_as_pd(stock_name, datefrom, dateto)
    stock_data = pd.merge(stock_data, current_stock_technicals, on='date')
    log.info("[{}] request market prices".format(stock_name))
    current_market_price = _request_market_prices_as_pd(stock_name, datefrom, dateto)
    stock_data = pd.merge(stock_data, current_market_price, on='date')
    log.info("[{}] request stock fundamentals".format(stock_name))
    current_stock_fundamentals = _request_stock_fundamentals_as_pd(stock_name, datefrom, dateto)
    stock_data = pd.merge(stock_data, current_stock_fundamentals, on='stock_name')
    stock_data = stock_data.query('(date >= start_date and date <= end_date)')
    stock_data = stock_data.drop(['start_date', 'end_date', 'fiscal_year', 'fiscal_period'], axis=1).reset_index(drop=True)
    return stock_data


# ======================================================================================================================
#                                                       STOCK PRICES
# ======================================================================================================================
def _request_stock_prices_as_pd(stock_name, datefrom, dateto):
    stock_daily = _request_stock_prices(stock_name, datefrom, dateto)
    stock_daily = pd.DataFrame(data=stock_daily, columns=['date', 'open', 'adj_open', 'close', 'adj_close', 'volume'])
    stock_daily = stock_daily.sort_values('date').reset_index(drop=True)
    stock_daily['close_prev1'] = stock_daily['close'].shift(1)
    stock_daily['adj_close_prev1'] = stock_daily['adj_close'].shift(1)
    stock_daily['volume_prev1'] = stock_daily['volume'].shift(1)
    stock_daily = stock_daily.assign(stock_name=stock_name)
    return stock_daily


def _request_stock_prices(stock_name, datefrom, dateto, page=None, verbose=False):
    params = {
        "api_key": _current_key,
        "start_date": datefrom.strftime("%Y-%m-%d"),
        "end_date": dateto.strftime("%Y-%m-%d"),
        "page": 100
    }
    if page is not None:
        params["next_page"] = page
    response = requests.request("get", "https://api-v2.intrinio.com/securities/{}/prices".format(stock_name),
                                params=params)
    if verbose and not response.ok:
        print("https://api-v2.intrinio.com/securities/{}/prices".format(stock_name))
        print(response.status_code)
        print(response.content)
    response = response.json()
    if 'error' in response:
        print(response['error'])
        print(response['message'])
    result = response["stock_prices"]
    for entry in result:
        entry['date'] = dtm.datetime.strptime(entry["date"], "%Y-%m-%d")
    if "next_page" in response and response["next_page"] is not None:
        result += (_request_stock_prices(stock_name, datefrom, dateto, response["next_page"]))
    return result


# ======================================================================================================================


# ======================================================================================================================
#                                                       STOCK TECHNICALS
# ======================================================================================================================
def _request_stock_technicals_as_pd(stock_name, datefrom, dateto):
    technicals = [('sma', {'period': 7}), ('sma', {'period': 14}), ('sma', {'period': 28}),
                  ('rsi', {'period': 7}), ('rsi', {'period': 14}), ('rsi', {'period': 28}),
                  ('obv', {}),
                  ('adi', {}),
                  ('adx', {'short_period': 3, 'long_period': 7}), ('adx', {'short_period': 7, 'long_period': 14}),
                  ('adx', {'short_period': 7, 'long_period': 28}),
                  ('bb', {}),
                  ('kc', {'period': 7}), ('kc', {'period': 14}),
                  ('kc', {'period': 28}), ]
    technicals_df = None
    for technical_name, kwargs in technicals:
        log.info((technical_name, kwargs))
        current_tech = _request_stock_technicals(stock_name, technical_name, datefrom, dateto, **kwargs)
        column_names = list(current_tech[0].keys())
        current_tech = pd.DataFrame(data=current_tech, columns=column_names)
        current_tech = current_tech.sort_values('date').reset_index(drop=True)
        # current_tech[technical_name] = current_tech[technical_name].shift(1)
        if len(column_names) > 2:
            column_names = ['-'.join([technical_name] + list(str(x) for x in kwargs.values()) + [column_name]) for column_name in column_names if column_name != 'date']
        else:
            column_names = ['-'.join([technical_name] + list(str(x) for x in kwargs.values()))]
        current_tech.columns = column_names + ['date']
        current_tech = current_tech[['date'] + column_names]
        if technicals_df is None:
            technicals_df = current_tech
        else:
            technicals_df = pd.merge(technicals_df, current_tech, on='date')
    return technicals_df


def _request_stock_technicals(stock_name, technical_name, datefrom, dateto, page=None, verbose=False, **kwargs):
    params = {
        "api_key": _current_key,
        "start_date": datefrom.strftime("%Y-%m-%d"),
        "end_date": dateto.strftime("%Y-%m-%d"),
        "price_key": "open",
        "page": 100
    }
    params = {**params, **kwargs}
    if page is not None:
        params["next_page"] = page
    response = requests.request("get", "https://api-v2.intrinio.com/securities/{}/prices/technicals/{}".format(stock_name, technical_name),
                                params=params)
    if verbose and not response.ok:
        print("https://api-v2.intrinio.com/securities/{}/prices/technicals/{}".format(stock_name, technical_name))
        print(response.status_code)
        print(response.content)
    response = response.json()
    if 'error' in response:
        print(response['error'])
        print(response['message'])
    result = response['technicals']
    for entry in result:
        entry_date = entry["date_time"].split('T')[0]
        entry['date'] = dtm.datetime.strptime(entry_date, "%Y-%m-%d")
        del entry["date_time"]
    if "next_page" in response and response["next_page"] is not None:
        result += _request_stock_technicals(stock_name, technical_name, datefrom, dateto, page=response["next_page"],
                                            **kwargs)
    return result


# ======================================================================================================================


# ======================================================================================================================
#                                                       MARKET STOCK PRICES
# ======================================================================================================================
def _request_market_prices_as_pd(stock_name, datefrom, dateto):
    market_daily = _request_market_prices('$SPX', datefrom, dateto)
    market_daily = pd.DataFrame(data=market_daily, columns=['date', 'close'])
    market_daily = market_daily.sort_values('date').reset_index(drop=True)
    market_daily['close'] = market_daily['close'].shift(1)
    market_daily.columns = ['date', 'market_close_prev1']
    return market_daily


def _request_market_prices(stock_name, datefrom, dateto, page=None, verbose=False):
    params = {
        "api_key": _current_key,
        "start_date": datefrom.strftime("%Y-%m-%d"),
        "end_date": dateto.strftime("%Y-%m-%d"),
        "page": 100
    }
    if page is not None:
        params["next_page"] = page
    response = requests.request("get",
                                "https://api-v2.intrinio.com/indices/stock_market/{}/historical_data/close_price"
                                .format(stock_name), params=params)
    if verbose and not response.ok:
        print("https://api-v2.intrinio.com/indices/stock_market/{}/historical_data/close_price".format(stock_name))
        print(response.status_code)
        print(response.content)
    response = response.json()
    if 'error' in response:
        print(f'stock_name={stock_name}, datefrom={datefrom}, dateto={dateto}, page={page}')
        print(response['error'])
        print(response['message'])
    result = response["historical_data"]
    for entry in result:
        entry['date'] = dtm.datetime.strptime(entry["date"], "%Y-%m-%d")
        entry['close'] = entry['value']
    if "next_page" in response and response["next_page"] is not None:
        result += _request_market_prices(stock_name, datefrom, dateto, response["next_page"])
    return result


# ======================================================================================================================


# ======================================================================================================================
#                                                       MARKET FUNDAMENTALS
# ======================================================================================================================
def _request_stock_fundamentals_as_pd(stock_name, datefrom, dateto):
    fiscal_years = list(range(datefrom.year - 1, dateto.year + 1))
    periods = ['Q1', 'Q2', 'Q3', 'Q4']
    calculations_reports = _request_stock_fundamentals_report_as_pd(stock_name, fiscal_years, periods)
    fundamentals = _request_stock_financial_fundamentals_as_pd(stock_name, fiscal_years, periods)
    fundamentals_report = pd.merge(fundamentals, calculations_reports, on=['fiscal_year', 'fiscal_period'])
    fundamentals_report = fundamentals_report.drop(['name', 'unit'], axis=1)
    fundamentals_report = pd.pivot_table(fundamentals_report,
                                         index=['start_date', 'end_date', 'fiscal_year', 'fiscal_period'],
                                         columns='tag', values='value').reset_index()
    fundamentals_report = fundamentals_report.assign(stock_name=stock_name)
    return fundamentals_report


def _request_stock_fundamentals_report_as_pd(stock_name, fiscal_years, periods):
    calculations_reports = pd.DataFrame(columns=['fiscal_year', 'fiscal_period', 'start_date', 'end_date'])
    for year in fiscal_years:
        curr_reports = _request_stock_fundamentals_report(stock_name, year)
        curr_reports = list(
            filter(lambda x: x['statement_code'] == 'calculations' and x['fiscal_period'] in periods, curr_reports))
        curr_reports = pd.DataFrame(data=curr_reports,
                                    columns=['fiscal_year', 'fiscal_period', 'start_date', 'end_date'])
        calculations_reports = pd.concat([calculations_reports, curr_reports])
    return calculations_reports


def _request_stock_fundamentals_report(stock_name, year, page=None, verbose=False):
    params = {
        "api_key": _current_key,
        "fiscal_year": year,
        "page": 100
    }
    if page is not None:
        params["next_page"] = page
    response = requests.request("get", "https://api-v2.intrinio.com/companies/{}/fundamentals".format(stock_name),
                                params=params)
    if verbose and not response.ok:
        print("https://api-v2.intrinio.com/companies/{}/fundamentals".format(stock_name))
        print(response.status_code)
        print(response.content)
    response = response.json()
    if 'error' in response:
        print(f'stock_name={stock_name}, year={year}, page={page}')
        print(response['error'])
        print(response['message'])
    result = response["fundamentals"]
    for entry in result:
        entry['start_date'] = dtm.datetime.strptime(entry["start_date"], "%Y-%m-%d") if entry[
                                                                                            "start_date"] is not None else None
        entry['end_date'] = dtm.datetime.strptime(entry["end_date"], "%Y-%m-%d") if entry[
                                                                                        "end_date"] is not None else None
    if "next_page" in response and response["next_page"] is not None:
        result += _request_stock_fundamentals_report(stock_name, year, response["next_page"])
    return result


def _request_stock_financial_fundamentals_as_pd(stock_name, fiscal_years, periods):
    tags = ['revenuegrowth', 'freecashflow', 'debt', 'bookvaluepershare', 'pricetobook', 'pricetoearnings',
            'evtoebitda',
            'ebitda', 'ebitdagrowth', 'grossmargin', 'efftaxrate', 'enterprisevalue', 'ltdebttoequity',
            'pricetoearnings', 'roic', 'roe', 'debttototalcapital', 'altmanzscore', 'pretaxincomemargin',
            'currentratio']
    fundamentals = None
    for year in fiscal_years:
        for period in periods:
            curr_fundamentals = _request_stock_financial_fundamentals(stock_name, 'calculations', year, period)
            if curr_fundamentals is None:
                continue
            curr_fundamentals = list(filter(lambda x: x['tag'] in tags, curr_fundamentals))
            curr_fundamentals = pd.DataFrame(data=curr_fundamentals, columns=['name', 'tag', 'unit', 'value'])
            curr_fundamentals['fiscal_year'] = year
            curr_fundamentals['fiscal_period'] = period
            if fundamentals is None:
                fundamentals = curr_fundamentals
            else:
                fundamentals = pd.concat([fundamentals, curr_fundamentals])
    return fundamentals


def _request_stock_financial_fundamentals(stock_name, fundamental, year, quarter, page=None, verbose=False):
    params = {
        "api_key": _current_key,
        "fiscal_year": year,
        "page": 100
    }
    if page is not None:
        params["next_page"] = page
    request_id = stock_name + '-' + fundamental + '-' + str(year) + '-' + quarter
    response = requests.request("get", "https://api-v2.intrinio.com/fundamentals/{}/standardized_financials"
                                .format(request_id), params=params)
    if verbose and not response.ok:
        print("https://api-v2.intrinio.com/fundamentals/{}/standardized_financials".format(request_id))
        print(response.status_code)
        print(response.content)
    response = response.json()
    if 'error' in response:
        print(f'stock_name={stock_name}, fundamental={fundamental}, year={year}, quarter={quarter}, page={page}')
        print(response['error'])
        print(response['message'])
    if "standardized_financials" not in response:
        return None
    result = response["standardized_financials"]
    result = [{'name': entry['data_tag']['name'], 'tag': entry['data_tag']['tag'], 'unit': entry['data_tag']['unit'],
               'value': entry['value']} for entry in result]
    if "next_page" in response and response["next_page"] is not None:
        result += _request_stock_financial_fundamentals(stock_name, fundamental, year, response["next_page"])
    return result


# ======================================================================================================================

if __name__ == '__main__':
    log.basicConfig(format='%(asctime)s - %(message)s', level=log.INFO)
    stock_names = ['MMM', 'AXP', 'AAPL', 'BA', 'CAT', 'CVX', 'CSCO', 'KO', 'XOM', 'GS',
                   'HD', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MRK', 'MSFT', 'NKE', 'PFE', 'PG',
                   'TRV', 'UNH', 'UTX', 'VZ', 'V', 'WMT', 'DIS']
    print(get_stocks_data(['MCD'], dtm.datetime(2019, 1, 1), dtm.datetime(2019, 3, 14)))
