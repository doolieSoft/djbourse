from django import forms

from .models import Stock, Transaction, CurrencyCurrentValue, Wallet
from .widgets import RelatedFieldWidgetCanAdd


class StockListForm(forms.Form):
    file = forms.FileField(label='Sélectionner le fichier')


class StockNewForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ("symbol", "name",)
        labels = {"symbol": "Symbole", "name": "Nom"}


class TransactionNewForm(forms.ModelForm):
    stock = forms.ModelChoiceField(
        label="Action",
        required=True,
        queryset=Stock.objects.all().order_by("name"),
        widget=RelatedFieldWidgetCanAdd(Stock, related_url="stock-create")
    )
    currency_current_value = forms.ModelChoiceField(
        label="Valeur devise étrangère",
        required=True,
        queryset=CurrencyCurrentValue.objects.all().order_by("-datetime_value"),
        widget=RelatedFieldWidgetCanAdd(CurrencyCurrentValue, related_url="currency-current-value-create")
    )
    wallet = forms.ModelChoiceField(
        label="Portefeuille",
        queryset=Wallet.objects.all().order_by("name"),
        required=True
    )

    class Meta:
        model = Transaction
        fields = (
        'date', 'nb', 'price_in_foreign_currency', 'transacrion_fees', 'stock', 'type', 'currency_current_value')
        labels = {'date': "Date", 'nb': "Nombre", 'price_in_foreign_currency': "Prix d'achat",
                  'transacrion_fees': "Frais d'opération", 'type': "Type"}


class CurrencyCurrentValueNewForm(forms.ModelForm):
    class Meta:
        model = CurrencyCurrentValue
        fields = ("ratio_foreign_to_home_currency", "datetime_value", "foreign_currency")
        labels = {"ratio_foreign_to_home_currency": "Taux de change",
                  "datetime_value": "Date valeur",
                  "foreign_currency": "Devise"}
