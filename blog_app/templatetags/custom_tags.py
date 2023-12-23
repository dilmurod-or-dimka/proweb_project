from django import template
from blog_app.models import Category
from blog_app.forms import CategoryForm
from django.shortcuts import redirect


register = template.Library()


@register.simple_tag()
def get_categories():
    categories = Category.objects.all()
    return categories

