from django.contrib import admin
from .models import Product, Order, OrderItem, Category
from .ai_utils import generate_description

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.action(description='Generate AI Descriptions')
def generate_ai_descriptions(modeladmin, request, queryset):
    for product in queryset:
        # In a real app, check for API key here
        new_desc = generate_description(product.name)
        product.description = new_desc
        product.save()
    
    modeladmin.message_user(request, f"Generated descriptions for {queryset.count()} products.")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    actions = [generate_ai_descriptions]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('user__username', 'stripe_payment_id')
    inlines = [OrderItemInline]
    readonly_fields = ('stripe_payment_id', 'created_at')
