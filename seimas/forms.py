from django import forms


class PrizeFrom(forms.Form):
    email = forms.EmailField(required=False)
