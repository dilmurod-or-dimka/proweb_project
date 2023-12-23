from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.


class Category(models.Model):
    title = models.CharField(verbose_name="Название категории", max_length=100)

    def get_absolute_url(self):
        return reverse("category_items", kwargs={"category_id": self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Recipe(models.Model):
    title = models.CharField(verbose_name="Название рецепта", max_length=150)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    views = models.IntegerField(verbose_name="Кол-во просмотров", default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    publish = models.BooleanField(verbose_name="Опубликовано ли?", default=True)
    description = models.TextField(verbose_name="Описание", default="")
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    image = models.ImageField(verbose_name="Фото", upload_to="photos/", blank=True, null=True, default=None)

    def get_absolute_url(self):
        return reverse("recipe_detail", kwargs={"recipe_id": self.pk})

    def __str__(self):
        return f"{self.author}: {self.title}"

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

# user.comments.


class Comment(models.Model):  # author, recipe, created_at, content
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()


class RecipeCountViews(models.Model):
    session_id = models.CharField(max_length=150, db_index=True, blank=True, null=True)
    user = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, null=True, blank=True, default=None, on_delete=models.CASCADE)

