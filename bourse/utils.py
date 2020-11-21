from .models import Stock, Price

LIMIT_BY_MINUTES = 5


def insert_new_stock_in_model(stock_file):
    stock_lines = stock_file.readlines()
    for stock_line in stock_lines:
        (symbol, name) = str(stock_line, 'utf-8').split(":")
        if not Stock.objects.filter(symbol=symbol).exists():
            s = Stock()
            s.symbol = str(symbol).strip()
            s.name = str(name).strip()
            s.save()


def get_prices_for_date(dt_from):
    stocks = Stock.objects.all()
    stocks_symbols_array = [stock.symbol for stock in stocks]

    prices_for_all_stocks = Price.objects.filter(date=dt_from, stock__symbol__in=stocks_symbols_array)

    price_by_symbol = {}
    for price in prices_for_all_stocks:
        price_by_symbol[price.stock.symbol] = price

    return price_by_symbol


def calculate_and_get_diff_for_period(prices_for_last_opened_day, prices_for_last_opened_day_of_period):
    result = {}
    for symbol, price in prices_for_last_opened_day.items():
        if symbol in prices_for_last_opened_day_of_period:
            diff = price.close - prices_for_last_opened_day_of_period[symbol].close
            pourcentage_diff = diff / price.close * 100
        else:
            pourcentage_diff = 0
        result[symbol] = pourcentage_diff

    return result


def get_differences_by_stock(differences_by_period, stock):
    line_by_stock = []
    for period in differences_by_period.keys():
        if stock.symbol not in differences_by_period[period]:
            line_by_stock.append("0.0")
        else:
            line_by_stock.append(round(differences_by_period[period][stock.symbol], 2))

    return {f"{stock.symbol} ({stock.name})": line_by_stock}
