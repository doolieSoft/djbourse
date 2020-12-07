from django.contrib import admin

from .models import StockPrice, Stock, Wallet, Transaction, AlphaVantageApiKey, Share, CurrencyDayValue, Currency


# Register your models here.
class ShareAdmin(admin.ModelAdmin):
    model = Share

    fields = ['nb', 'price_in_home_currency', 'price_in_foreign_currency', 'buy_date', 'wallet', 'stock',
              'currency_day_value', 'total_price_in_foreign_currency', 'total_price_in_home_currency']

    readonly_fields = ('total_price_in_foreign_currency', 'total_price_in_home_currency',)

    def total_price_in_foreign_currency(self, obj):
        return str(obj.total_price_in_foreign_currency) + " " + str(obj.currency_day_value.foreign_currency.symbol)

    def total_price_in_home_currency(self,obj):
        return str(obj.total_price_in_home_currency) + " €"

admin.site.register(Stock)
admin.site.register(StockPrice)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(AlphaVantageApiKey)
admin.site.register(Share, ShareAdmin)
admin.site.register(CurrencyDayValue)
admin.site.register(Currency)
