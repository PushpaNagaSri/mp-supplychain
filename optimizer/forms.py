from django import forms

class SupplyChainForm(forms.Form):
    name = forms.CharField(label='Product Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    demand = forms.IntegerField(label='Demand', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    supply = forms.IntegerField(label='Supply', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    cost = forms.IntegerField(label='Cost per Unit', widget=forms.NumberInput(attrs={'class': 'form-control'}))