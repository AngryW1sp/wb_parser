# Generated by Django 5.2.3 on 2025-07-03 11:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=256, unique=True, verbose_name='Поисковый запрос')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Название товара', max_length=256, verbose_name='Название')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('discounted_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена со скидкой')),
                ('rating', models.DecimalField(decimal_places=2, max_digits=3, verbose_name='Рейтинг')),
                ('supplier', models.CharField(blank=True, max_length=128, null=True, verbose_name='Поставщик')),
                ('reviews_count', models.PositiveIntegerField(blank=True, default=0, verbose_name='Количество отзывов')),
                ('search_query', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.searchquery')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['-rating', '-price'],
                'indexes': [models.Index(fields=['title'], name='products_pr_title_7d8124_idx'), models.Index(fields=['search_query'], name='products_pr_search__cc5c84_idx')],
                'unique_together': {('title', 'supplier', 'search_query')},
            },
        ),
    ]
