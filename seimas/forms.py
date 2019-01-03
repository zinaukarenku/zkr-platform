from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _

from seimas.models import Fraction, Committee


class PrizeFrom(forms.Form):
    email = forms.EmailField(required=False)


class PoliticianFiltersForm(forms.Form):
    fraction = forms.ModelChoiceField(
        label=_("Frakcija"),
        queryset=Fraction.objects.all(),
        empty_label=_("Pasirinkite frakciją"),
        required=False
    )

    committee = forms.ModelChoiceField(
        label=_("Komitetas"),
        queryset=Committee.objects.all(),
        empty_label=_("Pasirinkite komitetą"),
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
                Div('committee'),
                Div(Submit('filter', 'Filtruoti', css_class="btn btn-primary btn-block btn-sm"))
            )
        )

        self.is_valid()

    def get_selected_fraction(self):
        return self.cleaned_data.get('fraction')

    def get_selected_committee(self):
        return self.cleaned_data.get('committee')

    def filter_fraction(self, queryset, fraction):
        return queryset.filter(politician_fraction__fraction=fraction)

    def filter_committee(self, queryset, committee):
        return queryset.filter(politician_committees__committee=committee)

    def filter_queryset(self, queryset):
        fraction = self.get_selected_fraction()
        if fraction:
            queryset = self.filter_fraction(queryset, fraction)

        committee = self.get_selected_committee()
        if committee:
            queryset = self.filter_committee(queryset, committee)

        return queryset
