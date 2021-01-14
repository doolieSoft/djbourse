from django import forms

from .models import Stock


class StockListForm(forms.Form):
    file = forms.FileField(label='Sélectionner le fichier')


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ("symbol", "name",)
        labels = {"symbol": "Symbole", "name": "Nom"}
