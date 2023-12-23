from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeListView.as_view(), name="home"),
    path("categories/<int:category_id>/", views.category_items, name="category_items"),
    path("recipes/<int:recipe_id>/", views.recipe_detail, name="recipe_detail"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/registration/", views.registration_view, name="registration"),
    path("accounts/logout/", views.user_logout, name="logout"),

    path("create/", views.add_recipe, name="create"),
    path("update/<int:pk>/", views.UpdateRecipe.as_view(), name="update"),
    path("delete/<int:pk>/", views.DeleteRecipe.as_view(), name="delete"),

    path("search/", views.SearchResults.as_view(), name="search"),
    path("authors/<str:username>/", views.user_recipes, name="user_recipes"),
    path("comments/<int:comment_id>/delete/", views.del_comment, name="del_comment"),
    path("comments/<int:pk>/edit/", views.UpdateComment.as_view(), name="edit_comment"),
]
# http://127.0.0.1:8000/accounts/registration/
# http://127.0.0.1:8000/categories/2/
# http://127.0.0.1:8000/categories/3/
