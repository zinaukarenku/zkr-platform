from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django.forms import BooleanField, ModelForm, inlineformset_factory
from django.utils.safestring import mark_safe

from questions.models import PoliticianAnswer, Question
from django.utils.translation import gettext_lazy as _


class NewQuestionForm(ModelForm):
    check = BooleanField(
        required=True, initial=True, label="Sutinku su etikos kodeksu",
        help_text=mark_safe(
            '<a href="#kodeksas" data-toggle="modal" data-target="#kodeksas">Susipažinti su etikos kodeksu</a>')
    )

    class Meta:
        model = Question
        fields = ['politician', 'text', ]
        labels = {
            'politician': "Politikas",
            'text': "Klausimo tekstas"
        }
        help_texts = {
            'politician': None,
            'text': _(
                mark_safe(
                    "Siekiant užtikrinti informacijos prieinamumą ir tvarką, bei didesnį atsakytų klausimų skaičių, "
                    "<strong>klausimo apimtis ribojama iki 500 simbolių</strong>, įskaitant tarpus."))
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('politician'),
                Div('text'),
                Div('check'),
                Div(Submit('save', 'Publikuoti klausimą',
                           css_class='btn btn-bold btn-round btn-w-xl btn-primary float-right'),
                    ),
            ),
        )

        # self.fields['politician'].widget.choices = []


class PoliticianAnswerForm(ModelForm):
    class Meta:
        model = PoliticianAnswer
        fields = ['text', ]
        labels = {
            'text': "Atsakymas"
        }
        help_texts = {
            'text': "Po atsakymo publikavimo jo keisti nebegalėsite"

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Div('text'),
                Div(Submit('save', 'Publikuoti atsakymą',
                           css_class='btn btn-bold btn-round btn-w-xl btn-primary float-right'),
                    ),
            ),
        )


PoliticianAnswerFormSet = inlineformset_factory(Question, PoliticianAnswer, form=PoliticianAnswerForm)
