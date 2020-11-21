from django import forms


class StockListForm(forms.Form):
    file = forms.FileField(label='Sélectionner le fichier')
