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
from django.shortcuts import render
from .forms_qr import UrlParamForm
import qrcode
from io import BytesIO
import base64
from urllib.parse import urlencode
from django.http import HttpResponse

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
    #parent_category = category.parent ←すでにparentプロパティがあるので不要

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
    parent_id = content.category.parent_id
    parent_name = content.category.parent.name
    category_id = content.category.id
    category_name = Category.objects.filter(id=category_id).first().name


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
        "parent_id": parent_id,
        "parent_name": parent_name,
        "category_id": category_id,
        "category_name": category_name,
    })

@login_required_custom
def content_delete(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    content.delete()
    return redirect("parent_contents_default")  # 適切なリダイレクト先に変更

@login_required_custom
def category_add_tabs(request,):

    
    form = CategoryCreateForm()
    template_name = "category_add_tabs.html"

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
    })

@login_required_custom
def category_add_categories(request, parent_id: int):
    
    form = CategoryCreateForm()
    template_name = "category_add_categories.html"
    top_categories = Category.objects.filter(parent_id__isnull=True)
    parent_category = get_object_or_404(Category, id=parent_id)

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
        "parent_category": parent_category,
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


def content_view(request, content_id: int):
    content = get_object_or_404(Content, id=content_id)
    template_name = "content_view.html"

    return render(request, template_name, {
        "content": content,
    })

def search_results(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        results = Content.objects.filter(title__icontains=query).order_by("contents_display_order")

    return render(request, "search_results.html", {
        "query": query,
        "results": results,
    })

'''
def contents_all(request):
    contents_qs = (
        Content.objects
        .select_related("category")       # category.name をテンプレで使う前提
        .all()
        .order_by("contents_display_order") #表示順を追加
    )

    template_name = "contents_all.html"

    return render(request, template_name, {
        "contents": contents_qs,     # 右側テーブル
    })
'''

def contents_filtered_by_category(request, category_id: int,):
    category = get_object_or_404(Category, id=category_id)
    contents_qs = (
        Content.objects
        .select_related("category")       # category.name をテンプレで使う前提
        .filter(category=category)
        .order_by("id") #表示順を追加
    )
    print("contents_qs=",contents_qs)

    template_name = "contents_filtered_by_category.html"

    return render(request, template_name, {
        "contents": contents_qs,     # 右側テーブル
        "category": category,
    })

def all_contents(request):
    contents_qs = (
        Content.objects
        .select_related("category")       # category.name をテンプレで使う前提
        .all()
        .order_by("id") #表示順を追加
    )


    template_name = "all_contents.html"

    return render(request, template_name, {
        "all_contents": contents_qs,     
    })
    
def selected_contents(request):
    contents_qs = (
        Content.objects
        .select_related("category")       # category.name をテンプレで使う前提
        .all()
        .order_by("id") #表示順を追加
    )


    template_name = "all_contents.html"

    return render(request, template_name, {
        "all_contents": contents_qs,     
    })

def qr_generator(request):
    qr_base64 = None
    final_url = None

    if request.method == "POST":
        form = UrlParamForm(request.POST)
        if form.is_valid():
            base_url = form.cleaned_data['base_url']
            param_key_mkcd = form.cleaned_data['param_key_mkcd']
            param_value_mkcd = form.cleaned_data['param_value_mkcd']
            param_key_tscd = form.cleaned_data['param_key_tscd']
            param_value_tscd = form.cleaned_data['param_value_tscd']

            #1) 最終URLを組み立てる
            if param_key_mkcd and param_value_mkcd and param_key_tscd and param_value_tscd:
                query = urlencode({
                    param_key_mkcd: param_value_mkcd,
                    param_key_tscd: param_value_tscd,
                })
                final_url = f"{base_url}?{query}"
            else:
                final_url = base_url
            #2) QRコードを生成する
            qr = qrcode.QRCode(version=1, box_size=10, border=4,)
            qr.add_data(final_url)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            #3) 画像をメモリ上にPNGとして保存
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()

            #4) Base64に変換してテンプレートへ
            qr_base64 = base64.b64encode(img_bytes).decode('utf-8')
    else:
        form = UrlParamForm()

    context = {
        'form': form,
        'qr_base64': qr_base64,
        'final_url': final_url,
    }
    return render(request, 'qr_generator.html', context)

def qr_download(request):
    # GETパラメータからdataを受け取る想定 ?data=...
    data = request.GET.get("data")
    if not data:
        return HttpResponse("no data", status=400)

    # QRコード作成は上とほぼ同じ
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    # Content-Type と Content-Disposition を設定
    response = HttpResponse(img_bytes, content_type="image/png")
    response["Content-Disposition"] = 'attachment; filename="qrcode.png"'
    return response