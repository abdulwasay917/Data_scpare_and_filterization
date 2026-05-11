from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Category, Product, SubCategory
from .embeddings import get_similar_products


def index(request):
    categories = Category.objects.all()
    cat_data = []
    for cat in categories:
        product = None
        products = Product.objects.filter(category=cat)
        if products.exists():
            product = products.order_by("?").first()
        cat_data.append({"category": cat, "product": product})

    return render(request, "index.html", {
        "cat_data": cat_data
    })


def product(request, category_id=None):
    if category_id:
        category = get_object_or_404(Category, id=category_id)
    else:
        category = None
    if category:
        return render(request, "products.html", {
            "category": category,
            "subcategories": category.subcategories.all()
        })
    else:
        return render(request, "products.html", {
            "category": category,
        })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    similar_products = []

    try:
        candidates = Product.objects.filter(
            category=product.category
        ).exclude(id=product_id).filter(
            image__isnull=False
        )

        if candidates.exists():
            similar_products = get_similar_products(
                base_product=product,
                candidates=candidates,
                top_k=3
            )

    except Exception as e:
        print(f"Embedding error: {e}")

    return render(request, "product_details.html", {
        "product": product,
        "similar_products": similar_products[:3]
    })


def api_subcategories(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({"subcategories": []})

    subcategories = SubCategory.objects.filter(category_id=category_id)
    data = [
        {"id": s.id, "name": s.name}
        for s in subcategories
    ]
    return JsonResponse({"subcategories": data})


def filter_products(request):
    products = Product.objects.all()

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    subcategories = request.GET.get('subcategories', '')
    if subcategories:
        sub_ids = subcategories.split(",")
        sub_ids = [s.strip() for s in sub_ids if s]
        if sub_ids:
            products = products.filter(subcategory_id__in=sub_ids)

    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    search = request.GET.get('search')
    page = request.GET.get('page', 1)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if search:
        products = products.filter(product_name__icontains=search)
    sort = request.GET.get('sort', '')
    if sort == "low":
        products = products.order_by('price')
    elif sort == "high":
        products = products.order_by('-price')

    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(page)

    data = []
    for p in page_obj:
        data.append({
            "id": p.id,
            "product_name": p.product_name,
            "price": p.price,
            "image": p.image
        })

    return JsonResponse({
        "products": data,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number
    })