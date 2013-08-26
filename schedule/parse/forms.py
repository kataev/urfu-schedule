from django import forms
from .models import Group


class GroupSelectForm(forms.Form):
    group = forms.ModelChoiceField(Group.objects.all(), to_field_name='name')
