from django.urls import path
from . import views
from .views import (
    HomeView, ProductDetailView, CartView, CheckoutView, 
    CreateCheckoutSessionView, PaymentSuccessView, PaymentCancelView, StripeWebhookView, OrderHistoryView,
    AdminDashboardView, AboutView, ContactView, SignupView, 
    StoreLoginView, StoreLogoutView, SearchView,
    add_to_cart, update_cart, remove_from_cart, PaymentSimulationView, cancel_order
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add-to-cart'),
    path('cart/update/<str:item_id>/', update_cart, name='update-cart'),
    path('cart/remove/<str:item_id>/', remove_from_cart, name='remove-from-cart'),
    
    # Checkout & Payment
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('payment/simulate/', PaymentSimulationView.as_view(), name='payment-simulation'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payment/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Auth
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', StoreLoginView.as_view(), name='login'),
    path('logout/', StoreLogoutView.as_view(), name='logout'),
    path('search/', SearchView.as_view(), name='search'),
    path('order-history/', OrderHistoryView.as_view(), name='order-history'),
    path('order-history/cancel/<int:order_id>/', views.cancel_order, name='cancel-order'),
    path('health/', views.health_check, name='health-check'),
]
