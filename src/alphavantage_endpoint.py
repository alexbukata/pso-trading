import requests

API_KEY = '16RWHW72887PAH0C'
ALPHAVANTAGE_URL = 'https://www.alphavantage.co/query'


def get_market_data_daily():
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": "^GSPC",
        "outputsize": "full",
        "apikey": API_KEY
    }
    data = _request(ALPHAVANTAGE_URL, params)["Time Series (Daily)"]
    for key in data.keys():
        data[key]["open"] = float(data[key]["1. open"])
        data[key]["high"] = float(data[key]["2. high"])
        data[key]["low"] = float(data[key]["3. low"])
        data[key]["close"] = float(data[key]["4. close"])
        data[key]["volume"] = int(data[key]["5. volume"])
        del data[key]["1. open"]
        del data[key]["2. high"]
        del data[key]["3. low"]
        del data[key]["4. close"]
        del data[key]["5. volume"]
    return data


def _request(url, params):
    return requests.request("get", url, params=params).json()