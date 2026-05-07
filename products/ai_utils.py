import ollama
import json

from .models import Category, SubCategory


def classify_product(product_name):


    categories = list(
        Category.objects.values_list("name", flat=True)
    )

    subcategories = list(
        SubCategory.objects.values_list("name", flat=True)
    )


    response = ollama.chat(
        model="llama3",
        format="json",
        messages=[{
            "role": "user",
            "content": f"""
You are a professional ecommerce product classifier.

Your task is to classify the product into the MOST RELEVANT ecommerce category and subcategory.

IMPORTANT:
- Reuse existing categories/subcategories whenever possible
- Do NOT invent random categories
- Smartphones must go into Electronics > Smartphones
- iPhones are Smartphones
- Laptops are Computers
- Chairs/Sofas/Tables are Furniture

Existing Categories:
{categories}

Existing Subcategories:
{subcategories}

STRICT RULES:
- Return valid JSON only
- No explanation
- No notes
- No markdown
- category cannot be empty
- subcategory cannot be empty
- Only 1 category
- Only 1 subcategory

Product:
{product_name}

Output example:
{{"category":"Electronics","subcategory":"Smartphones"}}
"""
        }]
    )

    print(response["message"]["content"])
    try:
        data = json.loads(response["message"]["content"])

    except:
        data = {
            "category": "Miscellaneous",
            "subcategory": "General"
        }


    category_name = data["category"].strip()
    subcategory_name = data["subcategory"].strip()


    category_obj = Category.objects.filter(
        name__iexact=category_name
    ).first()

    if not category_obj:
        category_obj = Category.objects.filter(
            name__icontains=category_name
        ).first()

    if not category_obj:
        category_obj = Category.objects.create(
            name=category_name
        )


    subcategory_obj = SubCategory.objects.filter(
        name__iexact=subcategory_name,
        category=category_obj
    ).first()


    if not subcategory_obj:
        subcategory_obj = SubCategory.objects.create(
            name=subcategory_name,
            category=category_obj
        )



    return {
        "category": category_obj,
        "subcategory": subcategory_obj
    }