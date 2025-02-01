from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'subject', 'description', 'price', 'category', 'image')

from .models import Order, OrderItem

# OrderItem inline megjelenítése az Order admin felületén belül
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Nem jelenít meg üres sorokat feleslegesen

# Order admin konfiguráció
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'total_price', 'created_at')
    search_fields = ('full_name', 'email')
    list_filter = ('created_at',)
    inlines = [OrderItemInline]  # Megjeleníti az OrderItem-eket az Order admin oldalon belül

# OrderItem külön admin nézet (ha külön is akarod látni)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'price')
    search_fields = ('product__name',)
    list_filter = ('order__created_at',)