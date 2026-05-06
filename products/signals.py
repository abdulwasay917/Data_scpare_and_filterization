from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, Category, SubCategory
from .ai_utils import classify_product
from .embeddings import find_best_category


@receiver(post_save, sender=Product)
def auto_classify_product(sender, instance, created, **kwargs):
    if not created:
        return

    # STEP 1: fuzzy match
    category_obj = find_best_category(instance.product_name)

    # STEP 2: if no match → AI
    if not category_obj:
        ai_data = classify_product(instance.product_name)

        category_obj, _ = Category.objects.get_or_create(
            name=ai_data["category"]
        )
        subcat_name = ai_data["subcategory"]
    else:
        subcat_name = "General"

    # STEP 3: subcategory
    subcategory_obj, _ = SubCategory.objects.get_or_create(
        name=subcat_name,
        category=category_obj
    )

    # STEP 4: update product
    Product.objects.filter(id=instance.id).update(
        category=category_obj,
        subcategory=subcategory_obj
    )