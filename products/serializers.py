from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    search_query = serializers.SlugRelatedField(
        slug_field='value',
        read_only=True,
    )

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'price',
            'discounted_price',
            'rating',
            'supplier',
            'reviews_count',
            'search_query',
        )
        read_only_fields = ('id',)

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_discounted_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Discounted price cannot be negative."
            )
        return value
