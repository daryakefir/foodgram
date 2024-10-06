from django.contrib import admin
from django.contrib.admin import ModelAdmin

from recipes.mixins import AdminUserPermissionMixin
from recipes.models import MeasurementUnit, Ingredient, Tag, Recipe, IngredientsAmountInRecipe


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


@admin.register(Ingredient)
class IngredientAdmin(ModelAdmin, AdminUserPermissionMixin):
    """Класс для настройки админ-зоны модели Ingredient."""

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
       # 'measurement_unit',
        'amount',
    )
    list_filter = ('recipe','ingredients')
    search_fields = ('recipe',)
    list_display_links = ('recipe',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Класс для настройки админ-зоны модели Recipe."""

    ingredients = (IngredientAdmin,)

    list_display = (
        'id',
        'author',
        'name',
    )
    search_fields = ('author','name')
    list_filter = ('tags', )
    list_display_links = ('name',)
    empty_value_display = '-пусто-'

    def in_favorite(self, obj):
        return obj.favorite.all().count()

    in_favorite.short_description = 'Количество добавлений в избранное'
