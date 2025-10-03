from django.db import models

# Create your models here.

class Administrator(models.Model):
    """管理者情報"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        verbose_name="氏名",
        max_length=100
    )
    login_email = models.EmailField(
        verbose_name="ログインID（メールアドレス）",
        unique=True
    )
    password = models.CharField(
        max_length=50
    )

    class Meta:
        db_table = "管理者"
        verbose_name = "管理者"
        verbose_name_plural = "管理者"

    def __str__(self):
        return self.name


class Category(models.Model):
    """カテゴリ情報"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        verbose_name="カテゴリ名",
        max_length=100
    )
    parent_id = models.PositiveIntegerField(
        # "self",
        db_column="親カテゴリ",
        #　on_delete=models.SET_NULL,    親削除時に子を孤児化
        null=True, blank=True,
        # related_name="children"
    )

    @property
    def parent(self):
        """親カテゴリのオブジェクトを返す（なければNone）"""
        if self.parent_id:
            return Category.objects.filter(id=self.parent_id).first()
        return None

    class Meta:
        db_table = "カテゴリ"
        verbose_name = "カテゴリ"
        verbose_name_plural = "カテゴリ"

    def __str__(self):
        return self.name


class Content(models.Model):
    """コンテンツ情報"""
    id = models.AutoField(primary_key=True)
    administrator = models.ForeignKey(
        Administrator,
        on_delete=models.CASCADE,
        db_column="管理者ID"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        db_column="カテゴリID"
    )

    # 親カテゴリID
    @property
    def parent_category_id(self):
        return self.category.parent_id if self.category else None

    # 親カテゴリ名
    @property
    def parent_category_name(self):
        return self.category.parent.name if self.category and self.category.parent else None

    def __str__(self):
        return self.title

    title = models.CharField(
        verbose_name="表示名称（タイトル）",
        max_length=200
    )

    description = models.TextField(
        verbose_name="概要説明",
        blank=True, null=True
    )
    
    updater_user_id = models.PositiveIntegerField(
        verbose_name="更新者ID",
    )
    updated_at = models.DateTimeField(
        verbose_name="更新日",
        auto_now=True
    )
    file_url = models.URLField(
        verbose_name="添付ファイル格納先URL",
        max_length=500,
        blank=True, null=True
    )
    file_type = models.CharField(
        verbose_name="ファイル種別",
        max_length=50
    )

    class Meta:
        db_table = "コンテンツ"
        verbose_name = "コンテンツ"
        verbose_name_plural = "コンテンツ"

    def __str__(self):
        return self.title