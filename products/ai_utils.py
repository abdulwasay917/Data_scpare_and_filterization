import ollama
import json

def classify_product(product_name):
    response = ollama.chat(
        model="llama3",
        messages=[{
            "role": "user",
            "content": f"""
Return JSON only.

Product: {product_name}

Format:
{{"category": "", "subcategory": ""}}
"""
        }]
    )

    try:
        return json.loads(response["message"]["content"])
    except:
        return {"category": "Other", "subcategory": "General"}