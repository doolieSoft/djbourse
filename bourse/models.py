from django.db import models


# Create your models here.
class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=40)
    monitored = models.BooleanField(default=True)

    def __str__(self):
        return str(self.symbol) + " - " + str(self.name)


class Price(models.Model):
    open = models.FloatField()
    close = models.FloatField()
    date = models.DateField()
    stock = models.ForeignKey(to=Stock, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.stock.symbol) + " " + str(self.close) + " " + str(self.date)


class Wallet(models.Model):
    name = models.CharField(max_length=40)
    stocks = models.ManyToManyField(Stock)

    def __str__(self):
        return str(self.name)


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
