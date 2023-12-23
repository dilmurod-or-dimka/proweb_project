from django.contrib import admin

from .models import Category, Recipe


# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "title")
    list_display_links = ("pk", "title")


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "created_at", "views", "category", "author", "publish")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Recipe, RecipeAdmin)