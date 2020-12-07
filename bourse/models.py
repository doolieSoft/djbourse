from django.db import models


# Create your models here.
class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=40)
    monitored = models.BooleanField(default=True)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return str(self.symbol) + " - " + str(self.name)


class StockPrice(models.Model):
    open = models.FloatField()
    close = models.FloatField()
    date = models.DateField()
    stock = models.ForeignKey(to=Stock, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.stock.symbol) + " " + str(self.close) + " (" + str(self.date) + ")"


class Currency(models.Model):
    name = models.CharField(max_length=40)
    symbol = models.CharField(max_length=5)

    def __str__(self):
        return str(self.symbol) + " - " + str(self.name)


class CurrencyDayValue(models.Model):
    ratio_home_to_foreign_currency = models.FloatField()
    ratio_foreign_to_home_currency = models.FloatField()
    datetime_value = models.DateTimeField()
    foreign_currency = models.ForeignKey(to=Currency, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "1 " + str(self.foreign_currency.symbol) + " = " + str(
            self.ratio_foreign_to_home_currency) + " € (" + str(
            self.datetime_value) + ")"


class Wallet(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return str(self.name)


class Share(models.Model):
    nb = models.IntegerField()
    price_in_foreign_currency = models.FloatField()
    price_in_home_currency = models.FloatField()
    buy_date = models.DateField()
    wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE)
    stock = models.ForeignKey(to=Stock, on_delete=models.CASCADE)
    currency_day_value = models.ForeignKey(to=CurrencyDayValue, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.nb) + " " + str(self.stock.symbol) + " (" + str(self.buy_date) + ")"

    @property
    def total_price_in_foreign_currency(self):
        return round(self.price_in_foreign_currency * self.nb, 2)

    @property
    def total_price_in_home_currency(self):
        return round(self.price_in_home_currency * self.nb, 2)


VENTE = "Vente"
ACHAT = "Achat"
CHOICES_TYPE_TRANSACTION = ((ACHAT, "ACHAT"), (VENTE, "VENTE"),)


class Transaction(models.Model):
    date = models.DateField()
    quantity = models.IntegerField(default=0)
    stock = models.ForeignKey(Stock, on_delete=models.DO_NOTHING, null=True)
    total_value = models.FloatField(default=0)
    type = models.CharField(max_length=10, choices=CHOICES_TYPE_TRANSACTION, default=ACHAT)

    def __str__(self):
        return str(self.type) + " " + str(self.date) + " " + str(self.stock.symbol)


class AlphaVantageApiKey(models.Model):
    key = models.CharField(max_length=100)

    def __str__(self):
        return str(self.key)
