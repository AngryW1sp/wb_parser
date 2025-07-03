from celery import shared_task
from .models import Product, SearchQuery
from parser import WbParserCatalog, WbParserSearch


@shared_task
def parse_products_task(query=None, category_url=None, pages=None):
    if not query and not category_url:
        return "Не указан query или category_url"

    if query:
        parser = WbParserSearch(search_query=query, pages=pages)
        request_query = query.lower().strip()
    else:
        parser = WbParserCatalog(catalog_url=category_url, pages=pages)
        request_query = category_url.lower().strip()

    data = parser.parser()
    if not data:
        return "Нет данных для сохранения"

    search_query_obj, _ = SearchQuery.objects.get_or_create(
        value=request_query)
    Product.objects.filter(search_query=search_query_obj).delete()

    unique_products = {}
    for item in data:
        key = (item.get('name'), item.get('supplier', ''), search_query_obj.id)
        if key not in unique_products:
            unique_products[key] = Product(
                title=item.get('name'),
                price=item.get('price'),
                discounted_price=item.get('salePriceU'),
                rating=item.get('rating') or 0,
                supplier=item.get('supplier', ''),
                reviews_count=item.get('feedbacks') or 0,
                search_query=search_query_obj
            )
    Product.objects.bulk_create(unique_products.values())
    return f"Добавлено товаров: {len(unique_products)}"
