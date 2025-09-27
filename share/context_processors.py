# context_processors.py
from .models import Category

def parent_categories(request):
    """親カテゴリ一覧を常にテンプレートに渡す"""
    return {
        "parent_categories": Category.objects.filter(parent_id__isnull=True).order_by("name")
    }