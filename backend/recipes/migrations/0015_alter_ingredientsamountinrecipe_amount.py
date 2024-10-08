# Generated by Django 3.2.3 on 2024-10-06 18:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_rename_shopping_cart_shoppingcart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsamountinrecipe',
            name='amount',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество ингредиентов:1')]),
        ),
    ]