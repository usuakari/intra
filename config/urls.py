"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from share.views import TopView, KenshuView ,ToiawaseView ,
from share import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("parent/<int:parent_id>/", views.parent_contents, name="parent_contents"),
    path("category/<int:parent_id>/", views.parent_contents, name="parent_contents"),
    path("", views.parent_contents, {"parent_id": 8}, name="parent_contents_default"),
    path("content/add/<int:category_id>", views.category_contents, name="content_add"),
    path("content/edit/<int:content_id>", views.content_edit, name="edit"),
    path("content/<int:content_id>/delete/", views.content_delete, name="content_delete"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("category_add_tabs/", views.category_add_tabs, name="category_add_tabs"),
    path("category_add_categories/<int:parent_id>", views.category_add_categories, name="category_add_categories"),
    path("category_edit/", views.category_edit, name="category_edit"),
    path("content_add_with_category/<int:category_id>", views.content_add_with_category, name="content_add_with_category"),
    path("content_view/<int:content_id>", views.content_view, name="content_view"),
    path("search/", views.search_results, name="search_results"),
    path("contents/category/<int:category_id>/", views.contents_filtered_by_category, name="contents_filtered_by_category"),
    path("all_contents/", views.all_contents, name="all_contents"),
    path("selected_contents/", views.selected_contents, name="selected_contents"),
    path("qr_code_generator/", views.qr_code_generator, name="qr_code_generator"),
]
