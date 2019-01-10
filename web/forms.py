from allauth.account.forms import LoginForm as AllAuthLoginForm, ResetPasswordForm as AllAuthResetPasswordForm, \
    SignupForm as AllAuthSignupForm
from allauth.socialaccount.forms import SignupForm as AllAuthSocialSignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms
from django.utils.translation import gettext_lazy as _


class EmailSubscriptionForm(forms.Form):
    email = forms.EmailField()


class LoginForm(AllAuthLoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'sr-only'

        self.fields['login'].label = "El. paštas"
        self.fields['login'].widget.attrs['placeholder'] = "El. pašto adresas"
        self.fields['password'].label = "Slaptažodis"
        self.fields['password'].widget.attrs['placeholder'] = "Slaptažodis"


class SignupForm(AllAuthSignupForm):
    first_name = forms.CharField(min_length=2, max_length=30, label=_("Vardas"))
    last_name = forms.CharField(min_length=2, max_length=150, label=_("Pavardė"),
                                help_text=_("Pavardė viešai rodoma nebus"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('first_name', css_class='col-12'),
                Div('last_name', css_class='col-12'),
                Div('email', css_class='col-12'),
                Div('password1', css_class='col-12'),
                css_class='row'
            ),
        )

        self.fields['email'].label = "El. paštas"
        self.fields['email'].widget.attrs['placeholder'] = "El. pašto adresas"

        self.fields['password1'].label = "Slaptažodis"
        self.fields['password1'].widget.attrs['placeholder'] = self.fields['password1'].label

        self.fields['first_name'].widget.attrs['placeholder'] = self.fields['first_name'].label
        self.fields['last_name'].widget.attrs['placeholder'] = self.fields['last_name'].label

    def save(self, request):
        user = super().save(request)

        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name' '')
        user.save()
        return user


class ResetPasswordForm(AllAuthResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.fields['email'].label = "El. paštas"
        self.fields['email'].widget.attrs['placeholder'] = "El. pašto adresas"


class SocialSignupForm(AllAuthSocialSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.fields['email'].label = "El. paštas"
        self.fields['email'].widget.attrs['placeholder'] = "El. pašto adresas"
