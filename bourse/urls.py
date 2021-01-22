from django.urls import path, include

from .views import upload_stocks_symbol, \
    index, \
    show_stocks_followed, \
    unset_monitored, \
    set_monitored, \
    set_favorite, \
    unset_favorite, show_wallet_detail, \
    stock_create, \
    get_stock_id, \
    transaction_create, \
    currency_current_value_create, \
    get_currency_current_value_id

urlpatterns = [
    path('', index, name='index'),
    path('ajax/get_stock_id/', get_stock_id, name='get-stock-id'),
    path('ajax/get_currency_current_value_id/', get_currency_current_value_id, name='get-currency-current-value-id'),
    path('currency_current_value/create', currency_current_value_create, name="currency-current-value-create"),
    path('stock/create', stock_create, name="stock-create"),
    path('stocks/followed', show_stocks_followed, name='show-stocks-followed'),
    path('stocks/set_favorite', set_favorite, name='set-favorite'),
    path('stocks/set_monitored', set_monitored, name='set-monitored'),
    path('stocks/unset_favorite', unset_favorite, name='unset-favorite'),
    path('stocks/unset_monitored', unset_monitored, name='unset-monitored'),
    path('transaction/create', transaction_create, name='transaction-create'),
    path('upload_stocks_symbol', upload_stocks_symbol, name='upload-stocks-symbol'),
    path('wallet/detail/', show_wallet_detail, name='show-wallet-detail'),
]

#Add Django site authentication urls (for login, logout, password management)

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
