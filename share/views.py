# views.py
from django.shortcuts import render, get_object_or_404 , redirect
from django.views.generic import TemplateView , CreateView , UpdateView
from .models import Category, Content
from .forms import ContentForm , ContentCreateForm, CategoryCreateForm
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from functools import wraps
from django.http import HttpResponse
from django.forms import modelformset_factory

'''class TopView(TemplateView):
    template_name = "top.html"

class KenshuView(TemplateView):
    template_name = "kenshu.html"

class ToiawaseView(TemplateView):
    template_name = "toiawase.html"'''

def login_required_custom(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        else:
            return HttpResponse('不正な操作です', status=401) #不正な操作
        
    return _wrapped_view

def parent_contents(request, parent_id: int):
    parent = get_object_or_404(Category, id=parent_id)

    # 左メニュー用：この親にぶら下がる子カテゴリ
    children_qs = Category.objects.filter(parent_id=parent.id).order_by("category_display_order_leftmenues") #表示順を追加

    # 右側メイン：親配下（= 子カテゴリに属する）コンテンツを取得
    contents_qs = (
        Content.objects
        .select_related("category")       # category.name をテンプレで使う前提
        .filter(category__parent_id=parent.id)
        .order_by("contents_display_order") #表示順を追加
    )

    #1ファイルで共通化する方がメンテ性が高いので、固定名のテンプレに寄せます
    template_name = "parent_generic.html"

    return render(request, template_name, {
        "parent": parent,
        "children": children_qs,     # 左メニュー
        "contents": contents_qs,     # 右側テーブル
        # 子カテゴリごとにグルーピングしたい場合に便利な dict も渡しておく
        "contents_by_child": _group_by_child(contents_qs),
        "current_parent_id": parent_id,
    })


def _group_by_child(contents_qs):
    print("contents_qs=",contents_qs)
    """{child_category: [Content,...]} へ整形（テンプレ側で使いやすいように）"""
    from collections import OrderedDict
    grouped = OrderedDict()
    for c in contents_qs:
        grouped.setdefault(c.category, []).append(c)
        #print("c.category=",c.category)
    #print("grouped",grouped)
    return grouped

class ContentCreateView(CreateView):
    model = Content
    form_class = ContentForm
    template_name = "content_form.html"

    # success_url = reverse_lazy("top")  # 保存後にリダイレクトしたい先

@login_required_custom
def category_contents(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    form = ContentCreateForm()
    template_name = "content_form.html"

    if request.method == "POST":
        form = ContentCreateForm(request.POST)
        form.category = category         # ← POSTデータをバインド
        if form.is_valid():                         # ← バリデーション
            obj = form.save(commit=False)           # ← まだDBに書かない
            obj.category = category           # ← URLのカテゴリを紐づける（DB問い合わせ不要）
            # obj.updater_user_id = request.user.id # ← ログインIDを使うならここで上書き
            obj.save()                              # ← DBにINSERT
            return redirect("parent_contents_default")
        else : print("form errors", form.errors)
                        # ← 成功時はリダイレクト（任意）
    else:
        form = ContentCreateForm()

    return render(request, template_name, {
        "form": form,
        "category": category,
    })

@login_required_custom
def content_edit(request, content_id: int):
    nottop_categories = Category.objects.filter(parent_id__isnull=False)
    
    #print("nottop_categories",nottop_categories)
    
    content = get_object_or_404(Content, id=content_id)
    selected_top_category = Category.objects.filter(id=content.category.parent_id).first()
    form = ContentForm(instance=content)
    template_name = "content_edit.html"


    if request.method == "POST":
        form = ContentForm(request.POST, instance=content)
        form.content = content         # ← POSTデータをバインド
        if form.is_valid():                         # ← バリデーション
            obj = form.save(commit=False)           # ← まだDBに書かない
            obj.category = content.category          # ← URLのカテゴリを紐づける（DB問い合わせ不要）
            # obj.updater_user_id = request.user.id # ← ログインIDを使うならここで上書き
            obj.save()                              # ← DBにINSERT
            return redirect("parent_contents_default")
        else : print("form errors", form.errors)
    else:
        form = ContentForm(instance=content)

    return render(request, template_name, {
        "form": form,
        "content": content,
        "nottop_categories": nottop_categories,
        "selected_top_category": selected_top_category,
    })

@login_required_custom
def content_delete(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    content.delete()
    return redirect("parent_contents_default")  # 適切なリダイレクト先に変更

@login_required_custom
def category_add(request,):
    
    form = CategoryCreateForm()
    template_name = "category_add.html"
    top_categories = Category.objects.filter(parent_id__isnull=True)

    if request.method == "POST":
        data = request.POST.copy()
        print("POST内容:", request.POST)
        if data.get("parent_id"):
            data["parent_id"] = int(data["parent_id"])
            print("form parent_id=",request.POST.get("parent_id"))
            print("form name=",request.POST.get("name"))
            form = CategoryCreateForm(data)
        
        else:
            print("整数型でない（未選択など）")
            print("form parent_id=",request.POST.get("parent_id"))
            print("form name=",request.POST.get("name"))
            form = CategoryCreateForm(request.POST)

        if form.is_valid():                         # ← バリデーション
                obj = form.save(commit=False)           # ← まだDBに書かない
                # obj.updater_user_id = request.user.id # ← ログインIDを使うならここで上書き
                obj.save()                              # ← DBにINSERT
                return redirect("parent_contents_default")
        else : print("form errors", form.errors)
            
    else:
        form = CategoryCreateForm()

    return render(request, template_name, {
        "form": form,
        "top_categories": top_categories,
    })

@login_required_custom
def category_edit(request):
    template_name = "category_edit.html"

    # モデルフォームセットを作成（CategoryCreateFormをベースにする）
    CategoryFormSet = modelformset_factory(
        Category,
        form=CategoryCreateForm,
        extra=0,  # 既存データのみ（新規行は作らない）
        can_delete=True  # 削除用チェックボックスを追加
    )

    if request.method == "POST":
        formset = CategoryFormSet(request.POST)
        print("POST内容:", request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("parent_contents_default")
    else:
        formset = CategoryFormSet(queryset=Category.objects.all().order_by("id"))
        print("form errors", formset.errors)

    return render(request, template_name, {
        "formset": formset,
    })

class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = "login.html"

class LogoutView(LogoutView):
    template_name = "logged_out.html"

@login_required_custom
def content_add_with_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    parent_id = category.id

    if request.method == "POST":
        content_form = ContentCreateForm(request.POST)
        category_form = CategoryCreateForm(request.POST)

        if content_form.is_valid() and category_form.is_valid():
            # 新しいカテゴリを保存
            new_category = category_form.save()

            # コンテンツを新しいカテゴリに紐づけて保存
            content = content_form.save(commit=False)
            content.category = new_category
            content.save()

            return redirect("parent_contents_default")

    else:
        content_form = ContentCreateForm()
        category_form = CategoryCreateForm()

    return render(request, "content_add_with_category.html", {
        "content_form": content_form,
        "category_form": category_form,
        "category_id": category.id,   # ← ここは整数のまま渡す
        "parent_id": parent_id,
    })
