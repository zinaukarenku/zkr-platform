from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms
from allauth.account.forms import LoginForm as AllAuthLoginForm, SignupForm as AllAuthSignupForm, \
    ResetPasswordForm as AllAuthResetPasswordForm
from allauth.socialaccount.forms import SignupForm as AllAuthSocialSignupForm


class EmailSubscriptionForm(forms.Form):
    email = forms.EmailField()


class LoginForm(AllAuthLoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('login', css_class='col-12'),
                Div('password', css_class='col-12'),
                css_class='row'
            ),
        )


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


class ResetPasswordForm(AllAuthResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('email', css_class='col-12'),
                css_class='row'
            ),
        )


class SocialSignupForm(AllAuthSocialSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('email', css_class='col-12'),
                css_class='row'
            ),
        )
