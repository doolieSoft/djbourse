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


def get_prices_for_date(dt_from, stocks_symbols):
    price_by_symbol = {}
    for stock_symbol in stocks_symbols:
        nb_price_for_stock = StockPrice.objects.filter(date=dt_from, stock__symbol=stock_symbol).count()
        if nb_price_for_stock == 0:
            price_by_symbol[stock_symbol] = None
        else:
            price_by_symbol[stock_symbol] = StockPrice.objects.filter(date=dt_from, stock__symbol=stock_symbol)

    all_none = True
    for stock_symbol in stocks_symbols:
        if price_by_symbol[stock_symbol] is not None:
            all_none = False
            break

    if all_none == True:
        return None

    return price_by_symbol


def calculate_and_get_diff_for_period(prices_for_last_opened_day, prices_for_last_opened_day_of_period):
    result = {}
    for symbol, price in prices_for_last_opened_day.items():
        if prices_for_last_opened_day_of_period[symbol] is None:
            pourcentage_diff = ""
        else:
            diff = price[0].close - prices_for_last_opened_day_of_period[symbol][0].close
            pourcentage_diff = diff / prices_for_last_opened_day_of_period[symbol][0].close * 100

        result[symbol] = pourcentage_diff

    return result


def get_differences_by_stock(differences_by_period, stock):
    line_by_stock = []
    for period in differences_by_period.keys():
        if stock.symbol not in differences_by_period[period]:
            line_by_stock.append("")
        else:
            if isinstance(differences_by_period[period][stock.symbol], str):
                line_by_stock.append("")
            else:
                line_by_stock.append(round(differences_by_period[period][stock.symbol], 2))

    return {f"{stock.symbol} ({stock.name})": line_by_stock}
