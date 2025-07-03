from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'rating', 'discounted_price', 'reviews_count')
    search_fields = ('title',)
    list_filter = ('rating', 'reviews_count')
    ordering = ('-rating', 'price')
    list_per_page = 20