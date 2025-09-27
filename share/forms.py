# forms.py
from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = [
            "administrator",
            "category",
            "title",
            "description",
            "updater_user_id",
            "file_url",
            "file_type",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "file_url": forms.URLInput(attrs={"class": "form-control"}),
            "file_type": forms.TextInput(attrs={"class": "form-control"}),
            "updater_user_id": forms.NumberInput(attrs={"class": "form-control"}),
            "administrator": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }
