# context_processors.py
from .models import Category
from django.shortcuts import get_object_or_404
from django.http import HttpRequest

def parent_categories(request):
    """親カテゴリ一覧を常にテンプレートに渡す"""
    return {
        "parent_categories": Category.objects.filter(parent_id__isnull=True).order_by("category_display_order_tabs")
    }

def parent_id_processor(request):
    """現在の親カテゴリIDをテンプレートに渡す"""
    parent_id = request.resolver_match.kwargs.get("parent_id")
    return {
        "current_parent_id": parent_id
    }