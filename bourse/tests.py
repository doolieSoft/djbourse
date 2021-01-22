from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Stock, CurrencyCurrentValue, Currency, Share, Wallet
import pytz


class TestWalletDetail(TestCase):
    def setUp(self):
        self.date = datetime(2021, 1, 20, 00, 0, 0, 127325, tzinfo=pytz.UTC)
        self.user = User.objects.create_user("toto", password="toto")
        self.user.save()
        self.stock = Stock.objects.create(name="Test1", symbol="TST")
        self.stock.save()
        self.wallet = Wallet.objects.create(name="test", user=self.user)
        self.wallet.save()
        self.foreign_currency = Currency.objects.create(name="BOYARD", symbol="BRD")
        self.foreign_currency.save()
        self.currencyCurrentValue = CurrencyCurrentValue.objects.create(ratio_foreign_to_home_currency=0,
                                                                        datetime_value=self.date,
                                                                        foreign_currency=self.foreign_currency)
        self.currencyCurrentValue.save()
        self.share = Share.objects.create(nb=0, pmp_in_foreign_currency=0, wallet=self.wallet,
                                          currency_day_value=self.currencyCurrentValue, stock=self.stock)
        self.share.save()
