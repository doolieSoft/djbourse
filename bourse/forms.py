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


class DateInput(forms.DateInput):
    input_type = 'date'


class TransactionNewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.wallet = kwargs.pop('wallet')
        super(TransactionNewForm, self).__init__(*args, **kwargs)
        self.fields['wallet'].queryset = Wallet.objects.filter(id=self.wallet.id).order_by("name")

    stock = forms.ModelChoiceField(
        label="Action",
        required=True,
        queryset=Stock.objects.all().order_by("symbol"),
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
        queryset=Wallet.objects.all(),
        required=True
    )

    class Meta:
        model = Transaction
        fields = (
            'date', 'nb', 'price_in_foreign_currency', 'transaction_fees', 'stock', 'type', 'currency_current_value')
        labels = {'date': "Date", 'nb': "Nombre", 'price_in_foreign_currency': "Prix",
                  'transaction_fees': "Frais d'opération", 'type': "Type"}
        widgets = {
            'date': DateInput()
        }


class CurrencyCurrentValueNewForm(forms.ModelForm):
    class Meta:
        model = CurrencyCurrentValue
        fields = ("ratio_foreign_to_home_currency", "datetime_value", "foreign_currency")
        labels = {"ratio_foreign_to_home_currency": "Taux de change",
                  "datetime_value": "Date valeur",
                  "foreign_currency": "Devise"}
