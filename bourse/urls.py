from django.urls import path

from .views import upload_stocks_symbol, \
    index, \
    get_diff_for_all_periods_and_all_stocks, \
    add_stock_symbol, \
    add_transaction, \
    unset_monitored, \
    set_monitored, \
    set_favorite, \
    unset_favorite

urlpatterns = [
    path('', index, name='index'),
    path('get_diff_for_all_periods_and_all_stocks', get_diff_for_all_periods_and_all_stocks,
         name='get-diff-for-all-periods-and-all-stocks'),
    path('upload_stocks_symbol', upload_stocks_symbol, name='upload-stocks-symbol'),
    path('add_stock_symbol', add_stock_symbol, name='add-stock-symbol'),
    path('add_transaction', add_transaction, name='add-transaction'),
    path('unset_monitored', unset_monitored, name='unset-monitored'),
    path('set_monitored', set_monitored, name='set-monitored'),
    path('set_favorite', set_favorite, name='set-favorite'),
    path('unset_favorite', unset_favorite, name='unset-favorite')

]
