from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django import forms
from django.forms import BooleanField, ModelForm, inlineformset_factory
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from questions.models import PoliticianAnswer, Question
from django.utils.translation import gettext_lazy as _

from web.models import PoliticianInfo


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


class QuestionsListFiltersForm(forms.Form):
    status = forms.ChoiceField(
        label=_("Klausimo būsena"),
        choices=(
            ("visi", _("Visi")),
            ("atsakyti", _("Atsakyti")),
            ("neatsakyti", _("Neatsakyti")),
        ),
        required=False
    )

    politician = forms.ModelChoiceField(
        label=_("Politikas"),
        queryset=PoliticianInfo.objects.all(),
        to_field_name='pk',
        empty_label=_("Visi politikai"),
        required=False
    )

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)

        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Div(
                Div('status'),
                Div('politician'),
                Div(Submit('filter', 'Filtruoti', css_class="btn btn-primary btn-block btn-sm"))
            )
        )

        self.is_valid()

    def filter_status(self, queryset, status):
        if status == 'atsakyti':
            return queryset.filter_answered_questions()
        if status == 'neatsakyti':
            return queryset.exclude_answered_questions()

        return queryset

    def filter_politician(self, queryset, politician):
        return queryset.filter(politician=politician)

    def filter_queryset(self, queryset):
        status = self.cleaned_data.get('status')
        if status:
            queryset = self.filter_status(queryset, status)

        politician = self.cleaned_data.get('politician')
        if politician:
            queryset = self.filter_politician(queryset, politician)

        return queryset
