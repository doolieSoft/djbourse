from django.contrib import admin

from .models import Price, Stock, Wallet, Transaction

# Register your models here.
admin.site.register(Stock)
admin.site.register(Price)
admin.site.register(Wallet)
admin.site.register(Transaction)

