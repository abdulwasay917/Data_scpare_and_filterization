import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def get_embedding(text):
    return model.encode(text)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_similar_products(base_product, candidates, top_k):


    base_vec = get_embedding(base_product.product_name)

    scores = []
    for p in candidates:
        p_vec = get_embedding(p.product_name)
        sim = cosine_similarity(base_vec, p_vec)
        scores.append((p, sim))

    scores.sort(key=lambda x: x[1], reverse=True)

    return [p for p, _ in scores[:top_k]]