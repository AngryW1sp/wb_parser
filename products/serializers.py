from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
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
            'request_query',
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
