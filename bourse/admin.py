from django.contrib import admin

from .models import StockPrice, Stock, Wallet, Transaction, AlphaVantageApiKey, Share, CurrencyCurrentValue, Currency


# Register your models here.
class ShareAdmin(admin.ModelAdmin):
    model = Share

    fields = ['nb', 'pmp_in_foreign_currency', 'wallet', 'stock',
              'currency_day_value', 'total_price_in_foreign_currency', 'total_price_in_home_currency', 'archive']

    readonly_fields = ('total_price_in_foreign_currency', 'total_price_in_home_currency',)

    list_filter = ('archive',)

    def total_price_in_foreign_currency(self, obj):
        print(obj)
        return (str(obj.total_price_in_foreign_currency) + " " + str(obj.currency_day_value.foreign_currency.symbol)) or 0

    def total_price_in_home_currency(self,obj):
        print(obj)
        return (str(obj.total_price_in_home_currency) + " €") or 0

admin.site.register(Stock)
admin.site.register(StockPrice)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(AlphaVantageApiKey)
admin.site.register(Share, ShareAdmin)
admin.site.register(CurrencyCurrentValue)
admin.site.register(Currency)
