from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .ai_utils import classify_product

@receiver(post_save, sender=Product)
def auto_classify_product(sender, instance, created, **kwargs):
    if created:
        result = classify_product(instance.product_name)

        Product.objects.filter(id=instance.id).update(
            category=result["category"],
            subcategory=result["subcategory"]
        )