from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _

from seimas.models import Fraction


class PrizeFrom(forms.Form):
    email = forms.EmailField(required=False)


class PoliticianFiltersForm(forms.Form):
    fraction = forms.ModelChoiceField(
        label=_("Frakcija"),
        queryset=Fraction.objects.all(),
        empty_label=_("Pasirinkite frakciją"),
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
                Div('fraction'),
                Div(Submit('filter', 'Filtruoti'))
            )
        )

        self.is_valid()

    def get_selected_fraction(self):
        return self.cleaned_data.get('fraction')

    def filter_fraction(self, queryset, fraction):
        return queryset.filter(politician_fraction__fraction=fraction)

    def filter_queryset(self, queryset):
        fraction = self.get_selected_fraction()
        if fraction:
            queryset = self.filter_fraction(queryset, fraction)

        return queryset
