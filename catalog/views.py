from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Product
 
 
def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(
        is_active=True
    ).prefetch_related("images").order_by("-id")[:8]
    return render(request, "catalog/home.html", {
        "categories": categories,
        "featured_products": featured_products,
    })
 
 
def category_list(request):
    categories = Category.objects.all()
    return render(request, "catalog/category_list.html", {"categories": categories})
 
 
def product_list_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    categories = Category.objects.all()
 
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).prefetch_related("images")
 
    # --- Поиск ---
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )
 
    # --- Фильтры ---
    price_min = request.GET.get("price_min", "")
    price_max = request.GET.get("price_max", "")
    only_discount = request.GET.get("only_discount", "")
    in_stock = request.GET.get("in_stock", "")
    sort = request.GET.get("sort", "name")
 
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if only_discount:
        products = products.exclude(old_price__isnull=True).filter(old_price__gt=0)
    if in_stock:
        products = products.filter(stock__gt=0)
 
    sort_map = {
        "name": "name",
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-id",
    }
    products = products.order_by(sort_map.get(sort, "name"))
 
    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
 
    return render(request, "catalog/product_list.html", {
        "category": category,
        "categories": categories,
        "page_obj": page_obj,
        "products": page_obj,
        "q": q,
        "price_min": price_min,
        "price_max": price_max,
        "only_discount": only_discount,
        "in_stock": in_stock,
        "sort": sort,
    })
 
 
def product_list_all(request):
    """Все товары — страница Каталог"""
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).prefetch_related("images").select_related("category")
 
    # --- Поиск ---
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )
 
    # --- Фильтры ---
    cat_filter = request.GET.get("category", "")
    price_min = request.GET.get("price_min", "")
    price_max = request.GET.get("price_max", "")
    in_stock = request.GET.get("in_stock", "")
    only_discount = request.GET.get("only_discount", "")
    sort = request.GET.get("sort", "name")
 
    if cat_filter:
        products = products.filter(category__slug=cat_filter)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if in_stock:
        products = products.filter(stock__gt=0)
    if only_discount:
        products = products.exclude(old_price__isnull=True).filter(old_price__gt=0)
 
    sort_map = {
        "name": "name",
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-id",
    }
    products = products.order_by(sort_map.get(sort, "name"))
 
    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
 
    return render(request, "catalog/product_list_all.html", {
        "categories": categories,
        "page_obj": page_obj,
        "products": page_obj,
        "q": q,
        "cat_filter": cat_filter,
        "price_min": price_min,
        "price_max": price_max,
        "in_stock": in_stock,
        "only_discount": only_discount,
        "sort": sort,
    })
 
 
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        slug=slug,
        is_active=True
    )
    related = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).prefetch_related("images")[:4]
 
    return render(request, "catalog/product_detail.html", {
        "product": product,
        "related": related,
    })