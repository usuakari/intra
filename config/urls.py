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
from share.views import TopView, KenshuView ,ToiawaseView 
from share import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('share/kenshu.html',KenshuView.as_view(), name = "kenshu"),
    path('share/',ToiawaseView.as_view(), name = "toiawase"),
    path("parent/<int:parent_id>/", views.parent_contents, name="parent_contents"),
    path("category/<int:parent_id>/", views.parent_contents, name="parent_contents"),
    path("", views.parent_contents, {"parent_id": 8}, name="parent_contents_default"),

]
