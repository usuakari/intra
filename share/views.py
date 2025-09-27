# views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView , CreateView
from .models import Category, Content
from .forms import ContentForm

class TopView(TemplateView):
    template_name = "top.html"

class KenshuView(TemplateView):
    template_name = "kenshu.html"

class ToiawaseView(TemplateView):
    template_name = "toiawase.html"

def parent_contents(request, parent_id: int):
    parent = get_object_or_404(Category, id=parent_id)

    # 左メニュー用：この親にぶら下がる子カテゴリ
    children_qs = Category.objects.filter(parent_id=parent.id).order_by("name")

    # 右側メイン：親配下（= 子カテゴリに属する）コンテンツを取得
    contents_qs = (
        Content.objects
        .select_related("category")       # category.name をテンプレで使う前提
        .filter(category__parent_id=parent.id)
        .order_by("category__name", "-updated_at")
    )

    #1ファイルで共通化する方がメンテ性が高いので、固定名のテンプレに寄せます
    template_name = "parent_generic.html"

    return render(request, template_name, {
        "parent": parent,
        "children": children_qs,     # 左メニュー
        "contents": contents_qs,     # 右側テーブル
        # 子カテゴリごとにグルーピングしたい場合に便利な dict も渡しておく
        "contents_by_child": _group_by_child(contents_qs),
    })

def _group_by_child(contents_qs):
    """{child_category: [Content,...]} へ整形（テンプレ側で使いやすいように）"""
    from collections import OrderedDict
    grouped = OrderedDict()
    for c in contents_qs:
        grouped.setdefault(c.category, []).append(c)
    return grouped

class ContentCreateView(CreateView):
    model = Content
    form_class = ContentForm
    template_name = "content_form.html"

    # success_url = reverse_lazy("top")  # 保存後にリダイレクトしたい先

def category_contents(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    form = ContentForm()
    template_name = "content_form.html"

    return render(request, template_name, {
        "form": form,
        "category": category,
    })
