import json
import os.path
from datetime import datetime, timedelta

import requests as r

TIME_SERIES_INTRADAY = 'Time Series (5min)'
TIME_SERIES_DAILY = 'Time Series (Daily)'
OPEN = '1. open'
HIGH = '2. high'
LOW = '3. low'
CLOSE = '4. close'
VOLUME = '5. volume'


class StockPriceUpdater(object):

    def __init__(self, symbol, folder, api_key):
        self.api_key = api_key
        self.url = 'https://www.alphavantage.co/'
        self.query = 'query?function='
        self.p_series_type_daily = 'TIME_SERIES_DAILY'
        self.p_symbol = 'symbol=' + symbol
        self.p_interval = 'interval=5min'
        self.p_api_key = 'apikey=' + self.api_key
        self.symbol = symbol
        self.p_outputsize = 'outputsize=full'
        self.data = None
        self.folder = folder

    def download_data(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        if self.has_data(yesterday):
            with open(os.path.join(self.folder, f"{yesterday}-{self.symbol}.json"), "r") as json_file:
                json_data = json_file.read()
                self.data = json.loads(json_data)
            return os.path.join(self.folder, f"{yesterday}-{self.symbol}.json")
        else:
            # RECHERCHE des valeurs pour l'action p_symbol
            try:
                constructed_url = self.url + \
                                  self.query + \
                                  self.p_series_type_daily + \
                                  '&' + \
                                  self.p_symbol + \
                                  '&' + \
                                  self.p_interval + \
                                  '&' + \
                                  self.p_api_key + \
                                  '&' + \
                                  self.p_outputsize
                print(constructed_url)
                self.response = r.get(constructed_url)
                self.data = json.loads(self.response.text)

                if not os.path.isdir("data"):
                    os.mkdir("data")
                with open(os.path.join(self.folder, f"{yesterday}-{self.symbol}.json"), "w") as json_file:
                    json.dump(self.data, json_file)

                return os.path.join(self.folder, f"{yesterday}-{self.symbol}.json")
            except:
                print("Une erreur est apparue!")
                return None

    def get_symbol(self):
        return self.symbol

    def get_status(self):
        return self.response.status_code

    def get_open_value_for_date(self, date):
        date_formatted = date.strftime('%Y-%m-%d')
        # print(date_formatted)
        if date_formatted in self.data.get(TIME_SERIES_DAILY):
            return self.data.get(TIME_SERIES_DAILY).get(date_formatted).get(OPEN)
        else:
            yesterday_if_bourse_not_opened = date - timedelta(days=1)
            yesterday_if_bourse_not_opened_formatted = yesterday_if_bourse_not_opened.strftime(
                '%Y-%m-%d')
            while yesterday_if_bourse_not_opened_formatted not in self.data.get(TIME_SERIES_DAILY):
                yesterday_if_bourse_not_opened = yesterday_if_bourse_not_opened - timedelta(days=1)
                yesterday_if_bourse_not_opened_formatted = yesterday_if_bourse_not_opened.strftime(
                    '%Y-%m-%d')

            try:
                return self.data.get(TIME_SERIES_DAILY).get(yesterday_if_bourse_not_opened_formatted).get(OPEN)
            except:
                raise Exception(
                    "Open value doesn't exist for symbol {0} on this date : {1}".format(self.symbol, date_formatted))

    def get_percentage_diff(self, days):
        dt_to = datetime.now()

        dt_to_formatted = dt_to.strftime('%Y-%m-%d')
        while dt_to_formatted not in self.data[TIME_SERIES_DAILY]:
            dt_to = dt_to - timedelta(days=1)
            dt_to_formatted = dt_to.strftime('%Y-%m-%d')

        if dt_to.weekday() == 5:
            dt_to = dt_to - timedelta(days=1)
        elif dt_to.weekday() == 6:
            dt_to = dt_to - timedelta(days=2)

        dt_from = dt_to - timedelta(days=days)
        if dt_from.weekday() == 5:
            dt_from = dt_from - timedelta(days=1)
        elif dt_from.weekday() == 6:
            dt_from = dt_from - timedelta(days=2)

        try:
            to_open_value = self.get_open_value_for_date(dt_to)
            from_open_value = self.get_open_value_for_date(dt_from)
            difference = (float(to_open_value) -
                          float(from_open_value)) / float(from_open_value) * 100
            return difference
        except Exception as err:
            print("[ An exception occured ] " + str(err))
            raise err

    def has_data(self, date):
        return os.path.exists(os.path.join(self.folder, f"{date}-{self.symbol}.json"))
