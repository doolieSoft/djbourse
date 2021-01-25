from datetime import timedelta

from .models import Stock, StockPrice


def insert_new_stock_in_model(stock_file):
    stock_lines = stock_file.readlines()
    for stock_line in stock_lines:
        (symbol, name) = str(stock_line, 'utf-8').split(":")
        if not Stock.objects.filter(symbol=symbol).exists():
            s = Stock()
            s.symbol = str(symbol).strip()
            s.name = str(name).strip()
            s.save()


def get_price_for_date(dt_from, stock_symbol, best_effort=False):
    nb_price_for_stock = StockPrice.objects.filter(date=dt_from, stock__symbol=stock_symbol).count()

    if best_effort == False and nb_price_for_stock == 0:
        return dt_from, None

    i = 0
    over = False
    while nb_price_for_stock == 0:
        dt_from = dt_from - timedelta(days=1)
        nb_price_for_stock = StockPrice.objects.filter(date=dt_from, stock__symbol=stock_symbol).count()
        i += 1
        if i == 5:
            over= True
            break

    if over == True:
       return dt_from, None

    return  dt_from, StockPrice.objects.filter(date=dt_from,stock__symbol=stock_symbol).first().close


def calculate_and_get_diff_for_period(prices_for_last_opened_day, prices_for_last_opened_day_of_period):
    result = {}
    if prices_for_last_opened_day is None:
        return result

    for symbol, price in prices_for_last_opened_day.items():
        if symbol not in prices_for_last_opened_day_of_period:
            pourcentage_diff = ""
        elif prices_for_last_opened_day[symbol] is None:
            pourcentage_diff = ""
        elif symbol not in prices_for_last_opened_day_of_period:
            pourcentage_diff = ""
        elif prices_for_last_opened_day_of_period[symbol] is None:
            pourcentage_diff = ""
        else:
            diff = price - prices_for_last_opened_day_of_period[symbol]
            pourcentage_diff = diff / prices_for_last_opened_day_of_period[symbol] * 100

        result[symbol] = pourcentage_diff

    return result


def get_differences_by_stock(differences_by_period, stock):
    line_by_stock = []
    print(differences_by_period)
    for period in differences_by_period.keys():
        if stock.symbol in differences_by_period[period]:
            if isinstance(differences_by_period[period][stock.symbol], str):
                line_by_stock.append("")
            else:
                line_by_stock.append(round(differences_by_period[period][stock.symbol], 2))
        else:
            line_by_stock.append("")

    return {f"{stock.symbol} ({stock.name})": line_by_stock}
