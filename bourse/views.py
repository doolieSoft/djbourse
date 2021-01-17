import json
from datetime import datetime, timedelta

from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import CreateView

from .forms import StockListForm, StockNewForm, TransactionNewForm, CurrencyCurrentValueNewForm
from .models import Stock, AlphaVantageApiKey, Wallet, Share, StockPrice, \
    CurrencyCurrentValue, Transaction, Currency
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
def show_stocks_followed(request):
    dt_from = datetime.now()

    monitored_stocks = Stock.objects.filter(monitored=True)
    favorite_stocks = Stock.objects.filter(is_favorite=True)

    monitored_and_favorite_stocks_symbols = [stock.symbol for stock in monitored_stocks]
    monitored_and_favorite_stocks_symbols.extend([stock.symbol for stock in favorite_stocks])
    prices_for_last_opened_day = get_prices_for_date(dt_from, monitored_and_favorite_stocks_symbols)
    i = 0

    no_price_found = False
    while prices_for_last_opened_day is None:
        dt_from = dt_from - timedelta(days=1)
        prices_for_last_opened_day = get_prices_for_date(dt_from, monitored_and_favorite_stocks_symbols)
        i += 1
        if i > 5:
            no_price_found = True
            break

    differences_by_period = {}
    period_headers = {}
    for period in all_periods:
        dt_to = dt_from - timedelta(days=period)

        prices_for_last_opened_day_of_period = get_prices_for_date(dt_to, monitored_and_favorite_stocks_symbols)
        i = 0
        while prices_for_last_opened_day_of_period is None:
            dt_to = dt_to - timedelta(days=1)
            prices_for_last_opened_day_of_period = get_prices_for_date(dt_to, monitored_and_favorite_stocks_symbols)
            i += 1
            if i > 5:
                break

        diff_for_this_period = calculate_and_get_diff_for_period(prices_for_last_opened_day,
                                                                 prices_for_last_opened_day_of_period)

        differences_by_period[period] = diff_for_this_period
        period_headers[period] = period

    differences_by_monitored_stocks = []
    ordered_monitored_stocks = monitored_stocks.order_by('symbol')
    for stock in ordered_monitored_stocks:
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
    return render(request, "show_stock_followed.html", context)


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


class TransactionCreate(CreateView):
    model = Transaction
    form_class = TransactionNewForm
    template_name = 'add_transaction.html'
    success_url = "/"


def transaction_create(request):
    if request.method == "GET":
        form = TransactionNewForm()
        context = {"form": form}
        return render(request, 'add_transaction.html', context=context)

    elif request.method == "POST":
        form = TransactionNewForm(request.POST)
        if form.is_valid():
            share = Share.objects.filter(stock=form.cleaned_data["stock"]).first()
            if share is None:
                share = Share.objects.create(stock=form.cleaned_data["stock"],
                                             nb=form.cleaned_data["nb"],
                                             wallet=form.cleaned_data["wallet"],
                                             pmp_in_foreign_currency=form.cleaned_data["price_in_foreign_currency"],
                                             currency_day_value=form.cleaned_data["currency_current_value"])
                share.save()
                transaction = form.save()
                transaction.share = share
                transaction.save()
            else:
                total_pmp_price = share.nb * share.pmp_in_foreign_currency
                new_share_total_price = form.cleaned_data["nb"] * form.cleaned_data["price_in_foreign_currency"]
                new_nb_total_share = share.nb + form.cleaned_data["nb"]
                share.pmp_in_foreign_currency = (total_pmp_price + new_share_total_price) / new_nb_total_share
                share.nb = new_nb_total_share
                share.save()

                transaction = form.save()
                transaction.share = share
                transaction.save()

            return redirect("show-wallet-detail")
        else:
            return render(request, 'add_transaction.html', {"form": form})


def stock_create(request):
    print(request)
    if request.method == "GET":
        keys = AlphaVantageApiKey.objects.all()
        form = StockNewForm()
        if request.GET.get("popup"):
            context = {"keys": keys, "form": form, "popup": 1}
        else:
            context = {"keys": keys, "form": form}
        return render(request, 'add_stock.html', context=context)

    elif request.method == "POST":
        form = StockNewForm(request.POST)
        if form.is_valid():
            id = form.save()
            return HttpResponse(
                f'<script type="text/javascript">window.close(); window.opener.setDataStock("{id.pk}");</script>')
        else:
            return render(request, 'stock_form.html', {"form": form})


def get_stock_id(request):
    if request.method == "GET":
        return HttpResponse("OK")
    if request.is_ajax():
        id = request.POST['id']
        stock = Stock.objects.filter(pk=id)
        print(id)
        print(stock)
        data = serialize("json", stock, fields=("name"))
        return HttpResponse(data, content_type="application/json")


def currency_current_value_create(request):
    print(request.POST)
    if request.method == "GET":
        form = CurrencyCurrentValueNewForm()
        if request.GET.get("popup"):
            context = {"form": form, "popup": 1}
        else:
            context = {"form": form}
        return render(request, 'add_currency_current_value.html', context=context)

    elif request.method == "POST":
        form = CurrencyCurrentValueNewForm(request.POST)
        if form.is_valid():
            id = form.save()
            return HttpResponse(
                f'<script type="text/javascript">window.close(); window.opener.setDataCurrencyCurrentValue("{id.pk}");</script>')
        else:
            return render(request, 'add_currency_current_value.html', {"form": form})


def get_currency_current_value_id(request):
    if request.method == "GET":
        return HttpResponse("OK")
    if request.is_ajax():
        id = request.POST['id']
        print(id)
        currencyCurrentValue = CurrencyCurrentValue.objects.get(pk=id)
        print(str(currencyCurrentValue))
        currency = Currency.objects.get(pk=currencyCurrentValue.foreign_currency.id)
        response = json.dumps({"response": str(currencyCurrentValue)})

        return HttpResponse(response, content_type="application/json")


def unset_monitored(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = Stock.objects.get(symbol=symbol)
        stock.monitored = False
        stock.save()

    return redirect("show-stocks-followed")


def set_monitored(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = Stock.objects.get(symbol=symbol.strip())
        stock.monitored = True
        stock.save()
    return redirect("show-stocks-followed")


def set_favorite(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = Stock.objects.get(symbol=symbol.strip())
        stock.is_favorite = True
        stock.monitored = False
        stock.save()
    return redirect("show-stocks-followed")


def unset_favorite(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = Stock.objects.get(symbol=symbol.strip())
        stock.is_favorite = False
        stock.monitored = True
        stock.save()
    return redirect("show-stocks-followed")


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
            print(
                f"{transaction.nb} {transaction.price_in_foreign_currency} {transaction.currency_current_value.ratio_foreign_to_home_currency}")
            if transaction.type == "Vente":
                total_sell += transaction.nb * transaction.price_in_foreign_currency * transaction.currency_current_value.ratio_foreign_to_home_currency
            elif transaction.type == "Achat":
                total_buy += transaction.nb * transaction.price_in_foreign_currency * transaction.currency_current_value.ratio_foreign_to_home_currency

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
