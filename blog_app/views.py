from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import UpdateView, DeleteView, ListView
from django.core.mail import BadHeaderError

from .forms import LoginForm, RegistrationForm, RecipeForm, CommentForm, ContactForm
from .models import Recipe, Category, RecipeCountViews, Comment
from django.utils.datetime_safe import datetime
from django.contrib.auth.mixins import UserPassesTestMixin
import requests


# Create your views here.


class HomeListView(ListView):
    model = Recipe
    context_object_name = "items"
    template_name = "pages/index.html"


class SearchResults(HomeListView):
    def get_queryset(self):
        query = self.request.GET.get("q")
        return Recipe.objects.filter(
            Q(title__iregex=query) | Q(description__icontains=query)
        )


class UpdateRecipe(UserPassesTestMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "pages/post_form.html"

    def test_func(self):
        obj = self.get_object()
        return (obj.author == self.request.user) or self.request.user.is_superuser


class DeleteRecipe(DeleteView):
    model = Recipe
    success_url = "/"
    template_name = "pages/recipe_confirm_delete.html"


def home_view(request):
    items = Recipe.objects.all()
    context = {
        "items": items
    }
    return render(request, "pages/index.html", context)


def send_to_telegram(message):
    apiToken = '6340695368:AAEc_RX74Hb7zGpMB3gW_lLMT3ssw-v34N0'
    chatID = '-1001661400408'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            body = {
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "email": form.cleaned_data["email_address"],
                "message": form.cleaned_data["message"],
            }

            message = "\n".join(body.values())
            try:
                send_to_telegram(message)
            except BadHeaderError:
                return HttpResponse("Invalid header found")
            return redirect("home")
    else:
        form = ContactForm()

    context = {
        "form": form,
    }
    return render(request, "pages/index.html", context)


def category_items(request, category_id):
    category = Category.objects.get(pk=category_id)
    items = Recipe.objects.filter(category=category)
    context = {
        "items": items
    }
    return render(request, "pages/index.html", context)


def recipe_detail(request, recipe_id):
    item = Recipe.objects.get(pk=recipe_id)
    comments = item.comments.filter(recipe=item)

    if not request.session.session_key:
        request.session.save()

    session_id = request.session.session_key
    recipe_view = RecipeCountViews()
    recipe_view.recipe = item

    if not request.user.is_authenticated:
        recipe_views = RecipeCountViews.objects.filter(session_id=session_id, recipe=item)
        if not recipe_views.count() and str(session_id) != "None":
            recipe_view.session_id = session_id
    else:
        recipe_views = RecipeCountViews.objects.filter(user=request.user, recipe=item)
        if not recipe_views.count():
            recipe_view.user = request.user

    if recipe_view.session_id or recipe_view.user:
        recipe_view.save()
        item.views += 1
        item.save()

    if request.method == "POST":
        form = CommentForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.recipe = item
            form.save()
            return redirect("recipe_detail", item.pk)
    else:
        form = CommentForm()

    context = {
        "item": item,
        "form": form,
        "comments": comments
    }
    return render(request, "pages/recipe_detail.html", context)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = LoginForm()

    context = {
        "form": form
    }
    return render(request, "pages/login.html", context)


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistrationForm()
    context = {
        "form": form
    }
    return render(request, "pages/registration.html", context)


def user_logout(request):
    logout(request)
    return redirect("home")


def add_recipe(request):
    if request.method == "POST":
        form = RecipeForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect("recipe_detail", form.pk)
    else:
        form = RecipeForm()

    context = {
        "form": form
    }

    return render(request, "pages/post_form.html", context)


def user_recipes(request, username):
    user = User.objects.get(username=username)
    recipes = Recipe.objects.filter(author=user)
    total_views = sum([recipe.views for recipe in recipes])
    total_comments = sum([recipe.comments.all().count() for recipe in recipes])
    days = (datetime.now().date() - user.date_joined.date()).days

    context = {
        "username": username,
        'user': user,
        "items": recipes,
        "total_views": total_views,
        "total_comments": total_comments,
        "total_recipes": recipes.count,
        "days_left": days
    }
    return render(request, "pages/user_recipes.html", context)


def del_comment(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    if request.user == comment.author or request.user.is_superuser:
        recipe_id = comment.recipe.pk
        comment.delete()
        return redirect("recipe_detail", recipe_id)
    else:
        raise PermissionDenied


class UpdateComment(UserPassesTestMixin, UpdateView):
    model = Comment  # blog_app_comment
    template_name = "pages/recipe_detail.html"
    form_class = CommentForm

    def form_valid(self, form):
        obj = self.get_object()
        recipe = Recipe.objects.get(pk=obj.recipe.pk)
        form.save()
        return redirect("recipe_detail", recipe.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        recipe = Recipe.objects.get(pk=obj.recipe.pk)
        comments = Comment.objects.filter(recipe=recipe)
        context["item"] = recipe
        context["comments"] = comments
        return context

    def test_func(self):
        obj = self.get_object()
        return (obj.author == self.request.user) or self.request.user.is_superuser
