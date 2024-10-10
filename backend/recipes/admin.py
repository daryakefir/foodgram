from django.contrib import admin
from django.contrib.admin import ModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipes.mixins import AdminUserPermissionMixin
from recipes.models import (Favorite, Ingredient, IngredientsAmountInRecipe,
                            MeasurementUnit, Recipe, ShoppingCart, Tag)


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(ModelAdmin, AdminUserPermissionMixin):
    """Класс для настройки админ-зоны модели MeasurementUnit."""

    list_display = (
        'id',
        'name',
        'abbreviation',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    empty_value_display = '-пусто-'


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin, AdminUserPermissionMixin):
    """Класс для настройки админ-зоны модели Ingredient."""

    resource_class = IngredientResource
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(ModelAdmin, AdminUserPermissionMixin):
    """Класс для настройки админ-зоны модели Tag."""

    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    empty_value_display = '-пусто-'


@admin.register(IngredientsAmountInRecipe)
class IngredientsAmountInRecipeAdmin(ModelAdmin):
    """Класс для настройки админ-зоны модели IngredientsAmountInRecipe."""

    list_display = (
        'id',
        'recipe',
        'ingredients',
        'amount',
    )
    list_filter = ('recipe', 'ingredients')
    search_fields = ('recipe',)
    list_display_links = ('recipe',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Класс для настройки админ-зоны модели Recipe."""

    ingredients = (IngredientAdmin, )

    list_display = (
        'id',
        'author',
        'name',
    )
    search_fields = ('author', 'name')
    list_filter = ('tags', )
    list_display_links = ('name',)
    empty_value_display = '-пусто-'

    def in_favorite(self, obj):
        return obj.favorite.all().count()

    in_favorite.short_description = 'Количество добавлений в избранное'


@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    """Класс для настройки админ-зоны модели Favorite."""

    list_display = (
        'id',
        'recipe',
        'user',
    )
    search_fields = ('recipe', 'user')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    """Класс для настройки админ-зоны модели ShoppingCart."""

    list_display = (
        'id',
        'recipe',
        'user',
    )
    search_fields = ('recipe', 'user')
    empty_value_display = '-пусто-'
