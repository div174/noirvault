import random

def generate_description(product_name):
    """
    Simulates AI description generation if no API key is present.
    In a real scenario, this would call OpenAI's API.
    """
    
    adjectives = ["luxurious", "elegant", "sophisticated", "premium", "timeless", "refined", "exquisite"]
    verbs = ["crafted", "designed", "tailored", "curated", "created"]
    contexts = ["for the modern aesthete", "to elevate your wardrobe", "with impeccable attention to detail", "for those who appreciate quality"]
    
    adj1 = random.choice(adjectives).capitalize()
    adj2 = random.choice(adjectives)
    verb = random.choice(verbs)
    context = random.choice(contexts)
    
    # Template
    description = (
        f"Experience the {adj2} charm of the {product_name}. "
        f"{verb.capitalize()} with precision, this piece is {context}. "
        f"Perfect for making a statement while maintaining an air of understated elegance. "
        f"A true staple for any sophisticated collection."
    )
    
    return description
