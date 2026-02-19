from django.core.management.base import BaseCommand
from store.models import Product, Category
from django.utils.text import slugify
import random
import os

class Command(BaseCommand):
    help = 'Creates demo fashion products with realistic luxury names'

    def handle(self, *args, **kwargs):
        self.stdout.write('--- STRICT REBUILD: FLUSHING DATA ---')
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write('Database wiped.')

        base_dir = r'c:\Users\acer\Desktop\SG\project\media\products'
        categories = ['Men', 'Women', 'Accessories']
        
        category_objects = {}
        for cat_name in categories:
            cat, created = Category.objects.get_or_create(name=cat_name, slug=slugify(cat_name))
            category_objects[cat_name] = cat

        total_created = 0
        used_names = set()

        ADJECTIVES = [
            'Midnight', 'Obsidian', 'Charcoal', 'Slate', 'Matte', 
            'Velvet', 'Silk', 'Structured', 'Tailored', 'Oversized', 
            'Essential', 'Signature', 'Noir', 'Burnished', 'Heritage', 
            'Woven', 'Japanese', 'Italian', 'Heavyweight', 'Technical'
        ]
        
        # KEYWORD MAPPING - The key MUST be in the filename
        KEYWORD_MAP = {
            'blazer': ['Evening Blazer', 'Structured Jacket', 'Formal Blazer', 'Tuxedo Jacket'],
            'hoodie': ['Streetwear Hoodie', 'Fleece Pullover', 'Oversized Hoodie', 'Loopback Hoodie'],
            'shirt': ['Oxford Shirt', 'Linen Shirt', 'Poplin Shirt', 'Grandad Collar Shirt', 'Overshirt'],
            't-shirt': ['Mercerized Tee', 'Heavyweight Tee', 'Essential Tee', 'Boxy Fit Tee'],
            'jacket': ['Biker Jacket', 'Bomber Jacket', 'Field Jacket', 'Coach Jacket', 'Puffer'],
            'trousers': ['Pleated Trousers', 'Wool Trousers', 'Technical Cargo Pants', 'Tapered Chinos'],
            'chinos': ['Slim Fit Chinos', 'Cotton Twill Chinos'],
            'suit': ['3-Piece Suit', 'Wool Blend Suit', 'Tailored Suit'],
            'dress': ['Evening Gown', 'Silk Slip Dress', 'Maxi Dress', 'Cocktail Dress', 'Drape Dress'],
            'saree': ['Banarasi Saree', 'Silk Chiffon Saree', 'Embroidered Saree', 'Handloom Saree'],
            'kurti': ['Embroidered Kurti', 'Silk Tunic', 'Festive Kurta', 'Designer Kurti'],
            'skirt': ['Pleated Midi Skirt', 'Pencil Skirt', 'A-Line Skirt'],
            'top': ['Silk Blouse', 'Crop Top', 'Asymmetric Tunic'],
            'bag': ['Leather Tote', 'Crossbody Bag', 'Weekend Holdall', 'Messenger Bag'],
            'wallet': ['Bifold Wallet', 'Card Holder', 'Leather Billfold'],
            'belt': ['Leather Belt', 'Reversible Belt', 'Buckle Belt'],
            'watch': ['Chronograph Watch', 'Minimalist Watch', 'Automatic Diver'],
            'handbag': ['Structured Handbag', 'Leather Clutch', 'Shoulder Bag'],
            'scarf': ['Cashmere Scarf', 'Silk Scarf', 'Wool Wrap'],
            'glasses': ['Acetate Frames', 'Aviator Sunglasses', 'Wayfarer Shades'],
            'sunglasses': ['Acetate Frames', 'Aviator Sunglasses', 'Wayfarer Shades'],
            'shoe': ['Derby Shoes', 'Leather Loafers', 'Chelsea Boots', 'Low Top Sneakers'],
            'sneaker': ['Minimalist Sneakers', 'Retro Runners', 'High Top Sneakers'],
            'boot': ['Chelsea Boots', 'Combat Boots', 'Suede Desert Boots']
        }

        FALLBACK_NOUNS = ['Statement Piece', 'Essential Silhouette', 'Modern Classic', 'Utility Artifact', 'Design Object']

        def clean_filename(fname):
            return fname.lower().replace('-', '_').replace(' ', '_')

        for cat_name in categories:
            cat_dir = os.path.join(base_dir, cat_name.lower())
            if not os.path.exists(cat_dir):
                continue
                
            images = [f for f in os.listdir(cat_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            images.sort() # Verification stability
            
            for img_file in images:
                fname = clean_filename(img_file)
                
                # STRICT EXCLUSION
                if cat_name == 'Men':
                    if any(x in fname for x in ['dress', 'saree', 'skirt', 'gown', 'lehenga', 'kurti', 'women']):
                        self.stdout.write(f"SKIPPING MISMATCH: {img_file} in Men")
                        continue
                elif cat_name == 'Accessories':
                    if any(x in fname for x in ['saree', 'dress', 'shirt', 'pant', 'trousers', 'hoodie', 'blazer', 'jacket']):
                        self.stdout.write(f"SKIPPING MISMATCH: {img_file} in Accessories")
                        continue

                # Determine Noun
                noun = None
                for kw, options in KEYWORD_MAP.items():
                    if kw in fname:
                        noun = random.choice(options)
                        break
                
                if not noun:
                    # Fallback if no specific keyword found
                    # Do NOT use "Item" or "Product"
                    noun = random.choice(FALLBACK_NOUNS)
                
                # Generate Name
                adj = random.choice(ADJECTIVES)
                name = f"{adj} {noun}"
                
                # Duplicates
                tries = 0
                while name in used_names:
                    adj = random.choice(ADJECTIVES)
                    name = f"{adj} {noun}"
                    tries += 1
                    if tries > 5:
                        name = f"{name} {random.choice(['II', 'Edition', 'Pro'])}"
                
                used_names.add(name)

                # Price/Stock
                price = random.randint(1500, 15000)
                stock = random.randint(5, 50)
                
                # Path
                rel_path = os.path.join('products', cat_name.lower(), img_file).replace('\\', '/')
                
                Product.objects.create(
                    name=name,
                    description=f"A definitive {noun.lower()} from our {cat_name} collection. Meticulously crafted.",
                    price=price,
                    stock=stock,
                    image=rel_path,
                    category=category_objects[cat_name]
                )
                total_created += 1

        self.stdout.write(self.style.SUCCESS(f'Done. Created {total_created} unique luxury products.'))
