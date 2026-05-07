import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from sentence_transformers import SentenceTransformer
import numpy as np
from .models import Category

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Embedding model loaded successfully!")
except Exception as e:
    print(f"❌ Model load error: {e}")
    model = None


def find_best_category(product_name):
    if model is None:
        return None

    product_vec = model.encode(product_name)
    best_cat = None
    best_score = 0

    for cat in Category.objects.all():
        cat_vec = model.encode(cat.name)
        similarity = np.dot(product_vec, cat_vec) / (
            np.linalg.norm(product_vec) * np.linalg.norm(cat_vec)
        )

        if similarity > best_score:
            best_score = similarity
            best_cat = cat

    if best_score >= 0.30:
        return best_cat
    return None