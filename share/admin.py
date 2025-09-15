from django.contrib import admin
from .models import Administrator, Category, Content

# Register your models here.

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "parent_category_name", "parent_category_id")

    @admin.display(description="親カテゴリ名")
    def parent_category_name(self, obj):
        return obj.category.parent.name if obj.category and obj.category.parent else "-"

    @admin.display(description="親カテゴリID")
    def parent_category_id(self, obj):
        return obj.category.parent_id if obj.category else "-"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent_name", "parent_id_only")

    @admin.display(description="親カテゴリ")
    def parent_name(self, obj):
        return obj.parent.name if obj.parent else "-"

    @admin.display(description="親ID")
    def parent_id_only(self, obj):
        return obj.parent_id
    
@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "login_email")   # 一覧画面に表示する項目
    search_fields = ("name", "login_email")       # 検索ボックス用