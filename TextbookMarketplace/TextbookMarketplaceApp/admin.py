from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'subject', 'description', 'price', 'category', 'image')
