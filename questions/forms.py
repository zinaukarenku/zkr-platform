from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django.forms import ModelForm

from questions.models import Question


class NewQuestionForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Question
        fields = ['politician', 'text', ]
        labels = {
            'politician': "Politikas",
            'text': "Klausimo tekstas"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('politician'),
                Div('text'),
                Div('captcha'),
                Div(Submit('save', 'Publikuoti klausimą',
                           css_class='btn btn-bold btn-round btn-w-xl btn-primary float-right'),
                    ),
            ),
        )
