from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import Category

# Create your views here.

class TopView(TemplateView):
    template_name = "top.html"
    

class KenshuView(TemplateView):
    template_name = "kenshu.html"

class ToiawaseView(TemplateView):
    template_name = "toiawase.html"

def parent_contents(request, parent_id):
    parent = get_object_or_404(Category, id=parent_id)

    # テンプレートファイル名を動的に決める
    template_name = f"parent_{parent_id}.html"

    return render(request, template_name, {
        "parent": parent,
        "children": parent.children.all().prefetch_related("content_set"),
    })