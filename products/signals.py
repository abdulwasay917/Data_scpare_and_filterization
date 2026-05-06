from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .ai_utils import classify_product

@receiver(post_save, sender=Product)
def auto_classify_product(sender, instance, created, **kwargs):
    if created:  # sirf new product pe run hoga
        result = classify_product(instance.name)

        instance.category = result["category"]
        instance.subcategory = result["subcategory"]
        instance.save()