from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView, AdminRegisterView, add_to_cart, cart, checkout
from .views import AdminLoginView

urlpatterns = [
    path("",  views.product_list, name="products"),
        # User registration
    path('register/', RegisterView.as_view(), name='register'),
    path('cart/', cart, name='cart'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout'),


    # # Admin registration
    # path('admin/register/', AdminRegisterView.as_view(), name='admin_register'),

    # User Login and logout
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
        # Admin Login and logout
    path('admin/login/', AdminLoginView.as_view(), name='login'),
    path('admin/logout/', AdminLoginView.as_view(), name='logout')
]