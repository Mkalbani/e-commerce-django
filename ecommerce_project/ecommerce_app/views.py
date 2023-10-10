# Import necessary modules and classes
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.views.generic import FormView
from django.contrib.auth.views import LoginView
from .models import Product, Order, CartItem
from django import forms

# Define a view to handle user registration
class RegisterView(FormView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'

    def get_success_url(self):
        return reverse('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# Define a view for admin user registration
class AdminRegisterView(FormView):
    form_class = UserCreationForm
    template_name = 'registration/admin_register.html'

    def get_success_url(self):
        return reverse('admin:index')

    def form_valid(self, form):
        user = form.save()
        user.is_staff = True
        user.save()
        return super().form_valid(form)
    
# Define a view for admin user login
class AdminLoginView(LoginView):
    def get_success_url(self):
        return reverse('admin:index')

# Define a form for checkout
class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(max_length=255)
    billing_address = forms.CharField(max_length=255)

# Define a view to display a list of products
def product_list(request):
    products = Product.objects.all()
    return render(request, "ecommerce_app/index.html", {'products':products})

#Define a view to add to cart
@login_required
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    product = Product.objects.get(id=product_id)

    cart = request.session.get('cart', {})

    if type(cart) is dict:
        cart_item = CartItem(product=product)
        cart[product.id] = cart_item
    else:
        cart.add(product)

    request.session['cart'] = cart

    return redirect('cart')
# Define a view to display the user's cart
@login_required
def cart(request):
    cart = request.session.get('cart', {})
    total_price = 0
    for cart_item in cart:
        total_price += cart_item.product.price * cart_item.quantity

    context = {
        'cart': cart,
        'total_price': total_price,
    }

    return render(request, 'ecommerce_app/cart.html', context)

# Define a view to remove a product from the cart
@login_required
def remove_product(request, product_id):
    product = get_object_404(Product, pk=product_id)
    # Remove the product from the cart
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]

    # Update the session cart
    request.session['cart'] = cart

    # Redirect back to the product listing page
    return redirect('product_list')

# Define a view for the checkout process
@login_required
@login_required
def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create a new order
            order = Order()
            order.user = request.user
            order.shipping_address = form.cleaned_data['shipping_address']
            order.billing_address = form.cleaned_data['billing_address']
            order.save()

            # Add the cart items to the order
            cart = request.session.get('cart', {})
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, pk=product_id)
                order_item = OrderItem()
                order_item.order = order
                order_item.product = product
                order_item.quantity = quantity
                order_item.save()

            # Clear the session cart
            request.session['cart'] = {}

            # Redirect to the order confirmation page
            return redirect('order_confirmation', order.id)
    else:
        form = CheckoutForm()

    return render(request, 'ecommerce_app/checkout.html', {'form': form})

# Define a view to display the order confirmation
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'ecommerce_app/order_confirmation.html', {'order': order})

# Define a view to display the user's order history
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'ecommerce_app/order_history.html', {'orders': orders})

# Define a view to cancel an order
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.status = Order.STATUS_CANCELLED
    order.save()

    messages.success(request, 'Your order has been cancelled.')
    return redirect('order_history')
