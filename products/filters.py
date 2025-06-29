import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr='lte')
    min_rating = django_filters.NumberFilter(
        field_name="rating", lookup_expr='gte')
    max_rating = django_filters.NumberFilter(
        field_name="rating", lookup_expr='lte')
    min_reviews = django_filters.NumberFilter(
        field_name="reviews_count", lookup_expr='gte')
    max_reviews = django_filters.NumberFilter(
        field_name="reviews_count", lookup_expr='lte')
    request_query = django_filters.CharFilter(
        field_name="request_query", lookup_expr='exact')

    class Meta:
        model = Product
        fields = [
            'min_price', 'max_price', 'min_rating', 'max_rating',
            'min_reviews', 'max_reviews', 'request_query'
        ]
