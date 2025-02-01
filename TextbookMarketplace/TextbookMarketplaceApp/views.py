import os

from django.contrib.auth import login as auth_login, logout, login, update_session_auth_hash, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from .forms import SellNotesForm, RegistrationForm, EmailChangeForm, CheckoutForm
from .models import Product

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .models import (
    Product,
    Order,
    OrderItem
    )


class DeleteProductView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if product.seller != request.user:
            raise PermissionDenied
        if product.image:
            if os.path.isfile(product.image.path):
                os.remove(product.image.path)
        product.delete()
        #stfu
        return redirect('index')

class CheckoutView(LoginRequiredMixin, View):
    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        products = Product.objects.filter(id__in=cart.keys())
        cart_items = []
        total_price = 0

        for product in products:
            quantity = cart[str(product.id)]
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

        form = CheckoutForm()

        context = {
            'form': form,
            'cart_items': cart_items,
            'total_price': total_price
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        form = CheckoutForm(request.POST)

        if form.is_valid() and cart:
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = sum(
                Product.objects.get(id=int(pid)).price * qty for pid, qty in cart.items()
            )
            order.save()

            # Mentés az OrderItem táblába
            for product_id, quantity in cart.items():
                product = Product.objects.get(id=int(product_id))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            # Kosár ürítése
            request.session['cart'] = {}

            return render(request, 'order_success.html', {'order': order})

        return render(request, self.template_name, {'form': form})

class IndexView(TemplateView):
    template_name = 'index.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        if request.POST['searchtext']:
            searchtext = request.POST['searchtext']
            context['products'] = [o for o in context['products'] if o.contains_text(searchtext)]
            context['searchtext'] = searchtext
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['searchtext'] = ''
        return context


class MyProductsView(LoginRequiredMixin, TemplateView):
    template_name = 'my_products.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        if request.POST['searchtext']:
            searchtext = request.POST['searchtext']
            context['products'] = [o for o in context['products'] if o.contains_text(searchtext)]
            context['searchtext'] = searchtext
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(seller=self.request.user)
        return context


class SellProductView(LoginRequiredMixin, View):
    template_name = 'sell_product.html'
    form_class = SellNotesForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('index')
        else:
            return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'login.html'
    form_class = AuthenticationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('index')
        return render(request, self.template_name, {'form': form})


class RegistrationView(View):
    template_name = 'registration.html'
    form_class = RegistrationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        return render(request, self.template_name, {'form': form})

class SettingsView(LoginRequiredMixin, View):
    template_name = 'settings.html'

    def get(self, request, *args, **kwargs):
        form_pwdchange = PasswordChangeForm(request.user)
        form_emailchange = EmailChangeForm(request.user)
        return render(request, self.template_name, {
            'form_pwdchange': form_pwdchange,
            'form_emailchange': form_emailchange})

    def post(self, request, *args, **kwargs):
        form_pwdchange = PasswordChangeForm(user=request.user)
        form_emailchange = EmailChangeForm(user=request.user)
        if "pwdchange" in request.POST:
            form_pwdchange = PasswordChangeForm(user=request.user, data=request.POST)
            if form_pwdchange.is_valid():
                form_pwdchange.save()
                update_session_auth_hash(request, form_pwdchange.user)
                return redirect('index')
        elif "emailchange" in request.POST:
            form_emailchange = EmailChangeForm(user=request.user, data=request.POST)
            if form_emailchange.is_valid():
                form_emailchange.save()
                return redirect('index')
        elif "deluser" in request.POST:
            user_pk = request.user.pk
            logout(request)
            User = get_user_model()
            User.objects.filter(pk=user_pk).delete()
            return redirect('index')
        return render(request, self.template_name, {
            'form_pwdchange': form_pwdchange,
            'form_emailchange': form_emailchange})
            

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('index')


class ProductDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = kwargs.get('pk')
        context['product'] = get_object_or_404(Product, pk=pk)
        return context


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})

        # Kosár frissítése
        if str(product_id) in cart:
            cart[str(product_id)] += 1
        else:
            cart[str(product_id)] = 1

        request.session['cart'] = cart
        return redirect('cart')  # Kosár oldalra irányítás

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        cart = request.session.get('cart', {})

        # Ha létezik a termék a kosárban, töröljük
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart

        return redirect('cart')

class CheckoutView(LoginRequiredMixin, View):
    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        products = Product.objects.filter(id__in=cart.keys())

        cart_items = []
        total_price = 0

        for product in products:
            quantity = cart[str(product.id)]
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

        context = {
            'cart_items': cart_items,
            'total_price': total_price
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('cart')

        total_price = 0
        products = Product.objects.filter(id__in=cart.keys())

        # Rendelés létrehozása
        order = Order.objects.create(user=request.user, total_price=0)

        for product in products:
            quantity = cart[str(product.id)]
            subtotal = product.price * quantity
            total_price += subtotal

            # OrderItem létrehozása
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        order.total_price = total_price
        order.save()

        # Kosár ürítése
        request.session['cart'] = {}

        return render(request, 'order_success.html', {'order': order})

class CartView(LoginRequiredMixin, View):
    template_name = 'cart.html'

    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        products = Product.objects.filter(id__in=cart.keys())

        cart_items = []
        total_price = 0

        for product in products:
            quantity = cart[str(product.id)]
            subtotal = product.price * quantity
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

        context = {
            'cart_items': cart_items,
            'total_price': total_price
        }
        return render(request, self.template_name, context)
