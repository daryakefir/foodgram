from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """
    Регистронезависимая фильтрация объектов модели Ingredient
    по наименованию ингредиента.
    """

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтрация объектов модели Recipe по различным критериям."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.CharFilter(field_name='author')
    is_favorited = filters.BooleanFilter(method='filter_favorites_or_cart')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_favorites_or_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_favorites_or_cart(self, queryset, name, value):
        """
        Общий метод для фильтрации
        по нахождению в избранном или в списке покупок.
        """
        user = self.request.user
        if value and user.is_authenticated:
            if name == 'is_favorited':
                return queryset.filter(favorite__user=user)
            if name == 'is_in_shopping_cart':
                return queryset.filter(shoppingcart__user=user)
        return queryset
