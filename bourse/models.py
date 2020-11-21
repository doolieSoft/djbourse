from django.db import models


# Create your models here.
class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=40)

    def __str__(self):
        return str(self.symbol) + " - " + str(self.name)


class Price(models.Model):
    open = models.FloatField()
    close = models.FloatField()
    date = models.DateField()
    stock = models.ForeignKey(to=Stock, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.stock.symbol) + " " + str(self.close) + " " + str(self.date)
