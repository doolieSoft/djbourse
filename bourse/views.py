from datetime import datetime, timedelta

from django.shortcuts import redirect, render

from .forms import StockListForm
from .models import Stock, AlphaVantageApiKey, CHOICES_TYPE_TRANSACTION
from .utils import insert_new_stock_in_model, \
    calculate_and_get_diff_for_period, \
    get_differences_by_stock, \
    get_prices_for_date

DUREE_SEMAINE = float(7)
DUREE_MI_MOIS = float(14)
DUREE_3_SEMAINES = float(21)
DUREE_MOIS = float(30)
DUREE_BI_MOIS = float(60)
DUREE_MI_ANNEE = float(180)
DUREE_ANNEE = float(360)
DUREE_2_ANNEE = float(720)
all_periods = [DUREE_SEMAINE,
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

    array_of_array = []
    stocks = Stock.objects.filter(monitored=True).order_by('symbol')
    stocks_not_monitored = Stock.objects.filter(monitored=False).order_by('symbol')
    for stock in stocks:
        array_of_array.append(get_differences_by_stock(differences_by_period, stock))

    context = {
        "period_headers": period_headers,
        "array_of_array": array_of_array,
        "stocks_not_monitored": stocks_not_monitored
    }
    return render(request, "diff_for_all_periods_for_all_stocks.html", context)


def add_stock_symbol(request):
    keys = AlphaVantageApiKey.objects.all()
    context = {"keys": keys}
    return render(request, "add_stock_symbol.html", context=context)


def add_transaction(request):
    types_transaction = CHOICES_TYPE_TRANSACTION
    stocks = Stock.objects.all()
    context = {
        "stocks": stocks,
        "types_transaction":types_transaction
    }
    return render(request, "add_transaction.html", context=context)
