import json
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import StockListForm, StockForm
from .models import Stock, AlphaVantageApiKey, CHOICES_TYPE_TRANSACTION, Wallet, Share, StockPrice, \
    CurrencyCurrentValue, Transaction
from .utils import insert_new_stock_in_model, \
    calculate_and_get_diff_for_period, \
    get_differences_by_stock, \
    get_prices_for_date

DUREE_2_JOUR = float(2)
DUREE_SEMAINE = float(7)
DUREE_MI_MOIS = float(14)
DUREE_3_SEMAINES = float(21)
DUREE_MOIS = float(30)
DUREE_BI_MOIS = float(60)
DUREE_MI_ANNEE = float(180)
DUREE_ANNEE = float(360)
DUREE_2_ANNEE = float(720)
all_periods = [DUREE_2_JOUR,
               DUREE_SEMAINE,
               DUREE_MI_MOIS,
               DUREE_3_SEMAINES,
               DUREE_MOIS,
               DUREE_BI_MOIS,
               DUREE_MI_ANNEE,
               DUREE_ANNEE,
               DUREE_2_ANNEE]


def index(request):
    return render(request, 'index.html')


# cette méthode permet d'ajouter des actions "à suivre", à partir d'un fichier
def upload_stocks_symbol(request):
    message = ""

    if request.method == 'POST':
        form = StockListForm(request.POST, request.FILES)
        print(request.FILES['file'])

        if form.is_valid():
            fichier_actions = StockListForm()
            fichier_actions.file = form.cleaned_data['file']
            insert_new_stock_in_model(fichier_actions.file)

            return redirect('index')

        else:
            message = 'The form is not valid. Fix the following error:'

    else:
        form = StockListForm()  # An empty, unbound form

    context = {
        'form': form,
        'message': message
    }

    return render(request, 'upload_stocks_name.html', context)


# Cette méthode va calculer la différence en pourcentage par période
def get_diff_for_all_periods_and_all_stocks(request):
    dt_from = datetime.now()

    prices_for_last_opened_day = get_prices_for_date(dt_from)
    i = 0
    while not prices_for_last_opened_day:
        dt_from = dt_from - timedelta(days=1)
        prices_for_last_opened_day = get_prices_for_date(dt_from)
        i += 1
        if i > 5:
            break

    differences_by_period = {}
    period_headers = {}
    for period in all_periods:
        dt_to = dt_from - timedelta(days=period)

        prices_for_last_opened_day_of_period = get_prices_for_date(dt_to)
        i = 0
        while not prices_for_last_opened_day_of_period:
            dt_to = dt_to - timedelta(days=1)
            prices_for_last_opened_day_of_period = get_prices_for_date(dt_to)
            i += 1
            if i > 5:
                break

        diff_for_this_period = calculate_and_get_diff_for_period(prices_for_last_opened_day,
                                                                 prices_for_last_opened_day_of_period)

        differences_by_period[period] = diff_for_this_period
        period_headers[period] = period

    differences_by_monitored_stocks = []
    monitored_stocks = Stock.objects.filter(monitored=True).order_by('symbol')
    for stock in monitored_stocks:
        differences_by_monitored_stocks.append(get_differences_by_stock(differences_by_period, stock))

    stocks_not_monitored = []
    for stock in Stock.objects.filter(monitored=False, is_favorite=False).order_by('symbol'):
        stocks_not_monitored.append(f"{stock.symbol} ({stock.name})")

    differences_by_favorites_stocks = []
    favorites_stocks = Stock.objects.filter(is_favorite=True).order_by('symbol')
    for stock in favorites_stocks:
        differences_by_favorites_stocks.append(get_differences_by_stock(differences_by_period, stock))

    context = {
        "period_headers": period_headers,
        "differences_by_favorites_stocks": differences_by_favorites_stocks,
        "differences_by_monitored_stocks": differences_by_monitored_stocks,
        "stocks_not_monitored": stocks_not_monitored
    }
    return render(request, "diff_for_all_periods_for_all_stocks.html", context)


def add_stock_symbol(request):
    if request.method == "GET":
        keys = AlphaVantageApiKey.objects.all()
        context = {"keys": keys}
        return render(request, "add_stock_symbol.html", context=context)
    elif request.method == "POST":
        stock = Stock()
        stock.symbol = request.POST["symbol"].strip()
        stock.name = request.POST["name"].strip()
        stock.save()

        return redirect("index")


def add_transaction(request):
    types_transaction = CHOICES_TYPE_TRANSACTION
    stocks = Stock.objects.all()
    context = {
        "stocks": stocks,
        "types_transaction": types_transaction
    }
    return render(request, "add_transaction.html", context=context)


def stock_create_popup(request):
    form = StockForm(request.POST or None)
    if form.is_valid():
        instance = form.save()

        ## Change the value of the "#id_author". This is the element id in the form

        return HttpResponse(
            '<script>opener.closePopup(window, "%s", "%s", "#id_stock");</script>' % (instance.pk, instance))

    return render(request, "stock_form.html", {"form":form})

@csrf_exempt
def get_stock_id(request):
	if request.is_ajax():
		stock_name = request.GET['stock_name']
		stock_id = Stock.objects.get(name = stock_name).id
		data = {'stock_id':stock_id,}
		return HttpResponse(json.dumps(data), content_type='application/json')
	return HttpResponse("/")

def unset_monitored(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = Stock.objects.get(symbol=symbol)
        stock.monitored = False
        stock.save()

    return redirect("get-diff-for-all-periods-and-all-stocks")


def set_monitored(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = Stock.objects.get(symbol=symbol.strip())
        stock.monitored = True
        stock.save()
    return redirect("get-diff-for-all-periods-and-all-stocks")


def set_favorite(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = Stock.objects.get(symbol=symbol.strip())
        stock.is_favorite = True
        stock.monitored = False
        stock.save()
    return redirect("get-diff-for-all-periods-and-all-stocks")


def unset_favorite(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = Stock.objects.get(symbol=symbol.strip())
        stock.is_favorite = False
        stock.monitored = True
        stock.save()
    return redirect("get-diff-for-all-periods-and-all-stocks")


def show_wallet_detail(request):
    wallet = Wallet.objects.get(pk=1)

    shares = Share.objects.filter(wallet=wallet)
    transactions = Transaction.objects.all().order_by("-date")
    wallet_transactions = []
    total_buy = 0
    total_sell = 0
    total_transaction_fees = 0
    total_investment_in_stock = 0
    for transaction in transactions:
        if transaction.share.wallet == wallet:
            wallet_transactions.append(transaction)
            total_transaction_fees += round(transaction.transacrion_fees, 2)
            if transaction.type == "Vente":
                total_sell += round(
                    transaction.nb * transaction.price_in_foreign_currency * transaction.currency_transaction_value.ratio_foreign_to_home_currency,
                    2)
            elif transaction.type == "Achat":
                total_buy += round(
                    transaction.nb * transaction.price_in_foreign_currency * transaction.currency_transaction_value.ratio_foreign_to_home_currency,
                    2)

    shares_in_wallet_and_not_archived = shares.filter(wallet=wallet, archive=False).order_by('stock')

    current_shares_prices_by_stocks = {}
    current_total_prices_in_home_currency = {}
    shares_benef_by_stock = {}
    for share in shares_in_wallet_and_not_archived:
        stock_price = StockPrice.objects.filter(stock=share.stock).order_by("-date")
        current_shares_prices_by_stocks[share.stock.symbol] = stock_price[0].close

        currency_symbol = share.currency_day_value.foreign_currency.symbol
        most_recent_currency_day_value = \
            CurrencyCurrentValue.objects.filter(foreign_currency__symbol=currency_symbol).order_by("-datetime_value")[0]

        total_investment_in_stock += round(share.nb *
                                           stock_price[0].close *
                                           most_recent_currency_day_value.ratio_foreign_to_home_currency, 2)
        current_total_prices_in_home_currency[share.stock.symbol] = \
            round(share.nb *
                      stock_price[0].close *
                      most_recent_currency_day_value.ratio_foreign_to_home_currency, 2)

        benef = round((share.nb *
                       stock_price[0].close *
                       most_recent_currency_day_value.ratio_foreign_to_home_currency) - share.total_price_in_home_currency,
                      2)
        shares_benef_by_stock[share.stock.symbol] = benef

    shares_in_wallet_and_archived = Share.objects.filter(wallet=wallet, archive=True).order_by('stock')

    total_return = round(total_sell - total_buy + total_investment_in_stock - total_transaction_fees, 2)
    context = {
        'current_shares_prices_by_stocks': current_shares_prices_by_stocks,
        'current_total_prices_in_home_currency': current_total_prices_in_home_currency,
        'shares_benef_by_stock': shares_benef_by_stock,
        'shares': shares_in_wallet_and_not_archived,
        'shares_archived': shares_in_wallet_and_archived,
        'wallet': wallet,
        'transactions': wallet_transactions,
        'total_return': total_return
    }

    return render(request, "show_wallet_detail.html", context=context)
