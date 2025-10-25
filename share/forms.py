# forms.py
from django import forms
from .models import Content, Category

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = [
            "administrator",
            "category",
            "contents_display_order",
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
            "contents_display_order": forms.NumberInput(attrs={"class": "form-control"}),
        }

class ContentCreateForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = [
            "administrator",
            "title",
            "description",
            "updater_user_id",
            "contents_display_order",
            "file_url",
            "file_type",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "file_url": forms.URLInput(attrs={"class": "form-control"}),
            "file_type": forms.TextInput(attrs={"class": "form-control"}),
            "updater_user_id": forms.NumberInput(attrs={"class": "form-control"}),
            "contents_display_order": forms.NumberInput(attrs={"class": "form-control"}),
            "administrator": forms.Select(attrs={"class": "form-select"}),
        }

class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "id",
            "name", #カテゴリ名
            "parent_id", #親カテゴリID
            "category_display_order_tabs", #表示順(タブ)
            "category_display_order_leftmenues", #表示順(左メニュー)
        ]
        
        widgets = {
            "id": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "parent_id": forms.NumberInput(attrs={"class": "form-control"}),
            "category_display_order_tabs": forms.NumberInput(attrs={"class": "form-control"}),
            "category_display_order_leftmenues": forms.NumberInput(attrs={"class": "form-control"}),
        }