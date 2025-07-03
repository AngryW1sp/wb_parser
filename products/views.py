from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from .tasks import parse_products_task
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра и парсинга товаров.
    """
    queryset = Product.objects.select_related('search_query').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        """
        Получить список товаров с кэшированием на 5 минут.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='parse')
    def parse(self, request):
        """
        Запустить задачу парсинга товаров.
        """
        query = request.data.get('query')
        category_url = request.data.get('category_url')
        pages = request.data.get('pages', 50)

        if not query and not category_url:
            return Response(
                {"error": "Нужно указать либо 'query', либо 'category_url'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            task = parse_products_task.delay(
                query=query, category_url=category_url, pages=pages
            )
        except Exception as e:
            return Response(
                {"error": f"Ошибка запуска парсинга: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"task_id": task.id, "status": "Парсинг запущен в фоне"})
