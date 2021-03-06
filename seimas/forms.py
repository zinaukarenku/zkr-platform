from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _

from seimas.models import Fraction, Committee, Commission


class PrizeFrom(forms.Form):
    email = forms.EmailField(required=False)


class PoliticianFiltersForm(forms.Form):
    fraction = forms.ModelChoiceField(
        label=_("Frakcija"),
        queryset=Fraction.objects.all(),
        to_field_name='slug',
        empty_label=_("Pasirinkite frakciją"),
        required=False
    )

    committee = forms.ModelChoiceField(
        label=_("Komitetas arba pakomitetis"),
        queryset=Committee.objects.all(),
        to_field_name='slug',
        empty_label=_("Pasirinkite komitetą ar pakomitetį"),
        required=False
    )

    commission = forms.ModelChoiceField(
        label=_("Komisija"),
        queryset=Commission.objects.all(),
        to_field_name='slug',
        empty_label=_("Pasirinkite komisiją"),
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
                Div('committee'),
                Div('commission'),
                Div('fraction'),
                Div(Submit('filter', 'Filtruoti', css_class="btn btn-primary btn-block btn-sm"))
            )
        )

        self.is_valid()

    def filter_fraction(self, queryset, fraction):
        return queryset.filter(politician_fraction__fraction=fraction)

    def filter_committee(self, queryset, committee):
        return queryset.filter(politician_committees__committee=committee)

    def filter_commission(self, queryset, commission):
        return queryset.filter(politician_commissions__commission=commission)

    def filter_queryset(self, queryset):
        fraction = self.cleaned_data.get('fraction')
        if fraction:
            queryset = self.filter_fraction(queryset, fraction)

        committee = self.cleaned_data.get('committee')
        if committee:
            queryset = self.filter_committee(queryset, committee)

        commission = self.cleaned_data.get('commission')
        if commission:
            queryset = self.filter_commission(queryset, commission)

        return queryset
