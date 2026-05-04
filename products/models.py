from django.db import models


# ---------------- CATEGORY ---------------- #
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.name


# ---------------- SUBCATEGORY ---------------- #
class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.category.name} → {self.name}"


# ---------------- PRODUCT ---------------- #
class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    image = models.URLField(blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name