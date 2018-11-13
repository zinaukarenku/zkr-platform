from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms
from allauth.account.forms import LoginForm as AllAuthLoginForm, SignupForm as AllAuthSignupForm, \
    ResetPasswordForm as AllAuthResetPasswordForm
from allauth.socialaccount.forms import SignupForm as AllAuthSocialSignupForm
from snowpenguin.django.recaptcha3.fields import ReCaptchaField


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
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('email', css_class='col-12'),
                Div('password1', css_class='col-12'),
                Div('password2', css_class='col-12'),
                Div('captcha', css_class='col-12'),
                css_class='row'
            ),
        )

        self.fields['email'].label = "El. paštas"
        self.fields['email'].widget.attrs['placeholder'] = "El. pašto adresas"

        self.fields['password1'].label = "Slaptažodis"
        self.fields['password1'].widget.attrs['placeholder'] = self.fields['password1'].label

        self.fields['password2'].label = "Slaptažodis (dar kartą)"
        self.fields['password2'].widget.attrs['placeholder'] = self.fields['password2'].label


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
