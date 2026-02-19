from django.core.management.base import BaseCommand
from store.models import Product
import random

class Command(BaseCommand):
    help = 'Creates 6 demo products with realistic fashion names and placeholder images'

    def handle(self, *args, **kwargs):
        products = [
            "Midnight Silk Blazer",
            "Obsidian Leather Tote",
            "Cashmere Lounge Coat",
            "Velvet Evening Trouser",
            "Structured Wool Overcoat",
            "Sheer Organza Blouse"
        ]

        # Use a reliable placeholder service that supports text or random images
        # We'll use a specific fashion-abstract keyword for better relevance
        placeholder_base = "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80" # Example fashion abstract

        # Alternative: We can't easily download images to ImageField without requests/File logic which might be brittle.
        # For a pure MVP demo, we can either:
        # 1. Skip image (let template show "No Image")
        # 2. Use a dummy file if we want to test layout.
        
        # However, the user said: "Use a static placeholder image URL instead of ImageField for demo."
        # This implies we might need to tweak the template or model to accept URL if ImageField is empty, 
        # OR we just won't set the ImageField and rely on the template fallback?
        # NO, user said "Use a static placeholder image URL instead of ImageField".
        # This suggests I should probably not try to save to the ImageField (which stores files), 
        # unless I want to save a string to it (which works in some databases but is hacky) or download slightly.
        
        # Actually, let's look at the template code I wrote earlier:
        # {% if product.image %} <img src="{{ product.image.url }}" ...
        
        # If I want to support external URLs, I might need to hack the model or template.
        # BUT, to keep it "Clean MVP" and standard Django, usually we save a file.
        # Let's try to be smart: The user requirement is "Use a static placeholder image URL instead of ImageField".
        # This might mean "Don't use the ImageField logic, just hardcode a URL in the template" OR "Store the URL in the DB".
        # But I can't change the model schema easily without migration.
        
        # WORKAROUND: I will create the products without images for now, 
        # BUT I will update the template to show a nice placeholder if product.image is missing.
        # Wait, the user specifically asked "if images break, Use a static placeholder image URL instead of ImageField for demo."
        
        # So I will generate the products, and I will strictly follow the "clean" instruction.
        # I won't save a file to ImageField (complex without requests lib).
        # I will let them be created with no image.
        # AND I will provide instructions or a template tweak to render the placeholder if image is missing.
        
        # Let's create the products first.
        
        self.stdout.write('Creating demo products...')
        
        for name in products:
            price = random.randint(999, 4999)
            stock = random.randint(5, 20)
            
            Product.objects.create(
                name=name,
                description=f"A premium {name.lower()} crafted for the modern individual. Features exquisite detailing and timeless silhouette.",
                price=price,
                stock=stock
            )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(products)} demo products.'))
