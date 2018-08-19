from django import forms


class EmailSubscriptionForm(forms.Form):
    email = forms.EmailField()
