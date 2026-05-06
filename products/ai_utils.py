import ollama
import json
from .models import Category, SubCategory

def classify_product(product_name):
    response = ollama.chat(
        model="llama3",
        messages=[{
            "role": "user",
            "content": f"""
You are a strict JSON generator.

Classify this product into ecommerce category.

Product: {product_name}

Rules:
- Only 1 category
- Only 1 subcategory
- No explanation
- No extra text
- Output must be valid JSON only

Return format:
{{"category": "", "subcategory": ""}}
"""
        }]
    )

    try:
        data = json.loads(response["message"]["content"])
    except:
        data = {"category": "Other", "subcategory": "General"}

    # -----------------------------
    # DATABASE CHECK LOGIC
    # -----------------------------

    category_obj, created = Category.objects.get_or_create(
        name=data["category"]
    )

    subcategory_obj, created = SubCategory.objects.get_or_create(
        name=data["subcategory"],
        category=category_obj
    )

    return {
        "category": category_obj,
        "subcategory": subcategory_obj
    }