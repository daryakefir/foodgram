# Generated by Django 3.2.3 on 2024-10-02 15:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20240930_1543'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeIngredient',
            new_name='IngredientsAmountInRecipe',
        ),
    ]