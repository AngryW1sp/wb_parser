from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

app_name = 'products'

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
schema_view = get_schema_view(
    openapi.Info(
        title="WB Parser API",
        default_version='v1',
        description="Документация для вашего API",
    ),
    public=True,
)
urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui')
]
