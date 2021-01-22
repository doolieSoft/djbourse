import json
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import CreateView

from .forms import StockListForm, StockNewForm, TransactionNewForm, CurrencyCurrentValueNewForm
from .models import Stock, AlphaVantageApiKey, Wallet, Share, StockPrice, \
    CurrencyCurrentValue, Transaction, Currency, VENTE, StockFollowed
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


@login_required
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
@login_required
def show_stocks_followed(request):
    if request.method == "GET":
        dt_from = datetime.now()
        dt_from = dt_from - timedelta(days=1)

        followed_stocks = StockFollowed.objects.filter(user=request.user, is_favorite=False).order_by("stock__symbol")
        followed_and_favorite_stocks = StockFollowed.objects.filter(user=request.user)

        followed_and_favorite_stocks_symbols = []
        for followed_stock in followed_and_favorite_stocks:
            followed_and_favorite_stocks_symbols.append(followed_stock.stock.symbol)
        prices_for_last_opened_day = get_prices_for_date(dt_from, followed_and_favorite_stocks_symbols,
                                                         best_effort=True)

        differences_by_period = {}
        period_headers = {}
        for period in all_periods:
            dt_to = dt_from - timedelta(days=period)

            prices_for_last_opened_day_of_period = get_prices_for_date(dt_to, followed_and_favorite_stocks_symbols,
                                                                       best_effort=True)

            diff_for_this_period = calculate_and_get_diff_for_period(prices_for_last_opened_day,
                                                                     prices_for_last_opened_day_of_period)

            differences_by_period[period] = diff_for_this_period
            period_headers[period] = period

        differences_by_monitored_stocks = []

        for followed_stock in followed_stocks:
            differences_by_monitored_stocks.append(
                get_differences_by_stock(differences_by_period, followed_stock.stock))

        differences_by_favorites_stocks = []
        followed_favorites_stocks = StockFollowed.objects.filter(is_favorite=True).order_by('stock__symbol')
        for followed_stock in followed_favorites_stocks:
            differences_by_favorites_stocks.append(get_differences_by_stock(differences_by_period, followed_stock.stock))

        stocks_already_followed = StockFollowed.objects.filter(user=request.user)
        stocks_already_followed_symbol = {stock_already_followed.stock.symbol for stock_already_followed in stocks_already_followed}

        stocks_that_can_be_followed = Stock.objects.exclude(symbol__in=stocks_already_followed_symbol).order_by(
            "symbol")
        context = {
            "period_headers": period_headers,
            "differences_by_favorites_stocks": differences_by_favorites_stocks,
            "differences_by_monitored_stocks": differences_by_monitored_stocks,
            "stocks_that_can_be_followed": stocks_that_can_be_followed,
        }
        return render(request, "show_stock_followed.html", context)
    elif request.method == "POST":
        if StockFollowed.objects.filter(user=request.user, stock__id=request.POST["stock_id"]).count() == 0:
            stock = Stock.objects.get(id=request.POST["stock_id"])
            StockFollowed.objects.create(user=request.user, stock=stock)
        return redirect("show-stocks-followed")


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


@login_required
def transaction_create(request):
    current_user = request.user
    wallet = None
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(name="Mon portefeuille", user=current_user)
        wallet.save()

    if request.method == "GET":
        form = TransactionNewForm(wallet=wallet)
        context = {"form": form}
        return render(request, 'add_transaction.html', context=context)

    elif request.method == "POST":
        form = TransactionNewForm(request.POST, wallet=wallet)
        if form.is_valid():
            share = None
            try:
                share = Share.objects.get(stock=form.cleaned_data["stock"], wallet=wallet)
            except:
                pass

            if share is None:
                if form.cleaned_data["type"] == VENTE:
                    return render(request, "add_transaction.html",
                                  {"form": form, "error": "Vous n'avez aucune action à vendre."})

                # si achat et qu'il n'y a pas encore de share en db on la crée
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
                if form.cleaned_data["type"] == VENTE:
                    share.nb = share.nb - form.cleaned_data["nb"]
                    if share.nb == 0:
                        share.archive = True
                    elif share.nb < 0:
                        return render(request, "add_transaction.html",
                                      {"form": form, "error": "Vous n'avez pas assez d'action à vendre."})

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


@login_required
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
            if "popup" in request.GET:
                return HttpResponse(
                    f'<script type="text/javascript">window.close(); window.opener.setDataStock("{id.pk}");</script>')
            else:
                return redirect("index")
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
        StockFollowed.objects.filter(user=request.user, stock__symbol=symbol).delete()

    return redirect("show-stocks-followed")


def set_monitored(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")

        if StockFollowed.objects.filter(user=request.user, stock__symbol=symbol).count() == 0:
            StockFollowed.objects.create(user=request.user, stock__symbol=symbol)
    return redirect("show-stocks-followed")


def set_favorite(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = StockFollowed.objects.get(user=request.user, stock__symbol=symbol.strip())
        stock.is_favorite = True
        stock.save()
    return redirect("show-stocks-followed")


def unset_favorite(request):
    if request.method == "POST":
        symbol, name, *rest = request.POST['symbol'].split(" ")
        stock = StockFollowed.objects.get(user=request.user, stock__symbol=symbol.strip())
        stock.is_favorite = False
        stock.save()
    return redirect("show-stocks-followed")


@login_required
def show_wallet_detail(request):
    current_user = request.user
    wallet = None
    try:
        wallet = Wallet.objects.get(user=current_user.id)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(name="Mon portefeuille", user=current_user)
        wallet.save()

    transactions = Transaction.objects.filter(share__wallet__user=current_user).order_by("-date")
    wallet_transactions = []
    total_buy = 0
    total_sell = 0
    total_transaction_fees = 0
    total_investment_in_stock = 0
    for transaction in transactions:
        if transaction.share.wallet == wallet:
            wallet_transactions.append(transaction)
            total_transaction_fees += round(transaction.transaction_fees, 2)

            if transaction.type == "Vente":
                total_sell += transaction.nb * transaction.price_in_foreign_currency * transaction.currency_current_value.ratio_foreign_to_home_currency
            elif transaction.type == "Achat":
                total_buy += transaction.nb * transaction.price_in_foreign_currency * transaction.currency_current_value.ratio_foreign_to_home_currency

    shares_in_wallet_and_not_archived = Share.objects.filter(wallet=wallet, archive=False).order_by('stock__symbol')

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

    shares_in_wallet_and_archived = Share.objects.filter(wallet=wallet, archive=True).order_by('stock__symbol')

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
