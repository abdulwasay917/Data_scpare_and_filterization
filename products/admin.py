from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id","product_name","description", "price","image", "category","subcategory")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id","name","slug")

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("id","name","category")