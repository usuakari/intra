# app/forms_qr.py
from django import forms

class UrlParamForm(forms.Form):
    base_url = forms.URLField(label="ベースURL")
    param_key_mkcd = forms.CharField(label="お申込みコード", required=False)
    param_key_tscd = forms.CharField(label="担当者コード", required=False)
    param_value_mkcd = forms.CharField(label="お申込みコード値", required=False)
    param_value_tscd = forms.CharField(label="担当者コード値", required=False)
