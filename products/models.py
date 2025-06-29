from django.db import models


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

    request_query = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Поисковый запрос"
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-rating', '-price']
        unique_together = ('title', 'supplier', 'request_query')
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['request_query']),
        ]

    def __str__(self):
        return f"{self.title} - {self.discounted_price or self.price} ({self.rating})"
