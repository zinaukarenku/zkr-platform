from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.forms.utils import ErrorList

from web.models import Municipality
from django.utils.translation import gettext_lazy as _


class MayorCandidatesFiltersForm(forms.Form):
    municipality = forms.ModelChoiceField(
        label=_("Savivaldybė"),
        queryset=Municipality.objects.all(),
        to_field_name='slug',
        empty_label=_("Visos savivaldybės"),
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
                Div('municipality'),
                Div(Submit('filter', 'Filtruoti', css_class="btn btn-primary btn-block btn-sm"))
            )
        )

        self.is_valid()

    def filter_municipality(self, queryset, municipality):
        return queryset.filter(municipality=municipality)

    def filter_queryset(self, queryset):
        municipality = self.cleaned_data.get('municipality')
        if municipality:
            queryset = self.filter_municipality(queryset, municipality)

        return queryset
