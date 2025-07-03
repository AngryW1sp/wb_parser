from django.db import models


class SearchQuery(models.Model):
    value = models.CharField(max_length=256, unique=True,
                             verbose_name="Поисковый запрос")

    def __str__(self):
        return self.value


class Product(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name="Название",
        help_text="Название товара"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Цена со скидкой"
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name="Рейтинг"
    )
    supplier = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="Поставщик"
    )
    reviews_count = models.PositiveIntegerField(
        blank=True,
        default=0,
        verbose_name="Количество отзывов"
    )

    search_query = models.ForeignKey(
        SearchQuery, on_delete=models.CASCADE, related_name='products', )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-rating', '-price']
        unique_together = ('title', 'supplier', 'search_query')
        indexes = [
            models.Index(fields=['search_query']),
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
            models.Index(fields=['reviews_count']),

        ]

    def __str__(self):
        return f"{self.title} - {self.discounted_price or self.price} ({self.rating})"
