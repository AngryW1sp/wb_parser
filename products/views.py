from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from parser import WbParserCatalog, WbParserSearch


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    @action(detail=False, methods=['post'], url_path='parse')
    def parse_and_save(self, request):
        query = request.data.get('query')
        category_url = request.data.get('category_url')

        if not query and not category_url:
            return Response(
                {"error": "Нужно указать либо 'query', либо 'category_url'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if query:
            parser = WbParserSearch(search_query=query)
            request_query = query
        else:
            parser = WbParserCatalog(catalog_url=category_url)
            request_query = category_url

        data = parser.parser()
        if not data:
            return Response({"error": "Нет данных для сохранения."}, status=status.HTTP_204_NO_CONTENT)

        products_to_create = []
        for item in data:
            products_to_create.append(Product(
                title=item.get('name'),
                price=item.get('price'),
                discounted_price=item.get('salePriceU'),
                rating=item.get('rating') or 0,
                supplier=item.get('supplier', ''),
                reviews_count=item.get('feedbacks') or 0,
                request_query=request_query
            ))
        Product.objects.filter(request_query=request_query).delete()
        unique_products = {}
        for item in products_to_create:
            key = (item.title, item.supplier, item.request_query)
            if key not in unique_products:
                unique_products[key] = item

        Product.objects.bulk_create(unique_products.values())

        serializer = ProductSerializer(products_to_create, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='queries')
    def get_queries(self, request):
        queries = Product.objects.values_list('request_query', flat=True)
        # Уникализируем через set и убираем пустые значения
        unique_queries = sorted({q.strip()
                                for q in queries if q and q.strip()})
        return Response(unique_queries)
