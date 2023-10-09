from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import FormView
from django.contrib.auth.views import LoginView
from .models import Product, Order


class RegisterView(FormView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'

    def get_success_url(self):
        return reverse('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

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
    
class AdminLoginView(LoginView):
    def get_success_url(self):
        return reverse('admin:index')
    
# Created views.
def product_list(request):
    products = Product.objects.all()
    return render(request, "ecommerce_app/index.html", {'products':products})

@login_required
def add_to_cart(request):
    product = get_object_or_404(Product, pk=product_id)
    #Add product to cart
    cart  = request.session.get('cart', {})
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id]
    request.session['cart'] = cart
    return redirect('product_list')

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

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'ecommerce_app/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'ecommerce_app/order_history.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.status = Order.STATUS_CANCELLED
    order.save()

    messages.success(request, 'Your order has been cancelled.')
    return redirect('order_history')
