import argparse
import json
import os
# django project name is adleads, replace adleads with your project name
import time
from datetime import datetime

import requests as r
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

SECS_BEFORE_NEXT_API_CALL = 62

TIME_SERIES_DAILY = "Time Series (Daily)"
OPEN = "1. open"
CLOSE = "4. close"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djbourse.settings.prod")
import django

django.setup()

from utils.StockPriceUpdater import StockPriceUpdater
from bourse.models import Stock, StockPrice, CurrencyCurrentValue, Currency


def download_json_for_symbol(symbol, folder, api_key):
    spu = StockPriceUpdater(symbol, folder, api_key)
    file = spu.download_data()
    json_file = open(file, "r")
    return (file, json.load(json_file))


def update_exchange_rate_usd_to_eur():
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=EUR&apikey={args.api_key}"
    response = r.get(url)
    data = json.loads(response.text)
    print(data)
    try:
        foreign_currency = Currency.objects.get(symbol="$")
    except Currency.DoesNotExist:
        foreign_currency = Currency.objects.create(name="Dollar américain", symbol="$")
        foreign_currency.save()

    cdv = CurrencyCurrentValue()
    cdv.ratio_home_to_foreign_currency = 1 / float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    cdv.ratio_foreign_to_home_currency = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
    last_refreshed_datetime = data['Realtime Currency Exchange Rate']['6. Last Refreshed']
    dt = datetime.strptime(last_refreshed_datetime, "%Y-%m-%d %H:%M:%S")
    current_tz = timezone.get_current_timezone()
    last_refreshed_datetime = current_tz.localize(dt)
    cdv.datetime_value = last_refreshed_datetime
    cdv.foreign_currency = foreign_currency
    cdv.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--folder_data", type=str,
                        help="chemin complet du dossier contenant les json des actions téléchargé de alphavantage")
    parser.add_argument("--api_key", type=str,
                        help="Clé utilisée pour la connexion à alphavantage")

    args = parser.parse_args()

    if not args.folder_data:
        print(
            "Le paramètre folder_data ne peut être vide. Veuillez indiquer le chemin du dossier devant contenir les json")
        parser.print_help()
        exit(0)

    if not os.path.isdir(args.folder_data):
        os.mkdir(args.folder_data)

    if not args.api_key:
        print("Le paramètre api_key ne peut être vide. Veuillez indiquer la clé à utiliser")
        parser.print_help()
        exit(0)

    update_exchange_rate_usd_to_eur()

    stocks_symbols = Stock.objects.all().order_by("symbol")

    for stock_symbol in stocks_symbols:
        print(stock_symbol.name)
        (file, json_data) = download_json_for_symbol(stock_symbol.symbol, args.folder_data, args.api_key)

        if "Note" in json_data.keys():
            os.remove(file)
            print("Attente avant nouvel essai de download")
            time.sleep(SECS_BEFORE_NEXT_API_CALL)
            (file, json_data) = download_json_for_symbol(stock_symbol.symbol, args.folder_data, args.api_key)

        now = datetime.now()
        this_year = datetime.today().year
        first_day_of_this_year = f"{this_year}-01-01"

        print(file)
        if StockPrice.objects.filter(stock=stock_symbol).count() == 0:
            if TIME_SERIES_DAILY in json_data:
                for date, prices in json_data[TIME_SERIES_DAILY].items():
                    price_date = f"{date}"
                    price_open = f"{float(prices[OPEN]):.2f}"
                    price_close = f"{float(prices[CLOSE]):.2f}"

                    price = StockPrice()
                    price.open = price_open
                    price.close = price_close
                    price.date = price_date
                    price.stock = stock_symbol
                    price.save()
        else:
            for date, prices in json_data[TIME_SERIES_DAILY].items():
                if date > first_day_of_this_year:
                    if StockPrice.objects.filter(date=date, stock=stock_symbol).count() == 0:
                        price_date = f"{date}"
                        price_open = f"{float(prices[OPEN]):.2f}"
                        price_close = f"{float(prices[CLOSE]):.2f}"

                        price = StockPrice()
                        price.open = price_open
                        price.close = price_close
                        price.date = price_date
                        price.stock = stock_symbol
                        price.save()
