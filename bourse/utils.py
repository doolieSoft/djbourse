from .models import Stock

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
