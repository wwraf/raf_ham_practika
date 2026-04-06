from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.product_list_all, name="shop"),
    path("catalog/", views.category_list, name="category_list"),
    path("catalog/<slug:slug>/", views.product_list_by_category, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]