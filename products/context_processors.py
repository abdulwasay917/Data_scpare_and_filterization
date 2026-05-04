from .models import Category

def header_data(request):
    categories = Category.objects.prefetch_related("subcategories").all()
    return {
        "header_categories": categories
    }