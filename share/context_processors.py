# context_processors.py
from .models import Category
from django.shortcuts import get_object_or_404
from django.http import HttpRequest

def parent_categories(request):
    """親カテゴリ一覧を常にテンプレートに渡す"""
    return {
        "parent_categories": Category.objects.filter(parent_id__isnull=True).order_by("category_display_order_tabs")
    }

def current_ids_processor(request):
    """親カテゴリID・カテゴリIDの両方をテンプレートに渡す"""
    match = request.resolver_match
    if not match:
        return {}

    kwargs = match.kwargs

    return {
        "current_parent_id": kwargs.get("parent_id"),
        "current_category_id": kwargs.get("category_id"),
    }
