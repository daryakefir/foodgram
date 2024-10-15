import pyshorteners
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from api.filters import IngredientFilter, RecipeFilter
from api.serializers import (IngredientSerializer, RecipeGetSerializer,
                             RecipeWriteSerializer, TagSerializer)
from core.paginations import ApiPagination
from core.permissions import (IsAdminOrReadOnly,
                              IsOwnerAdminOrReadOnlyPermission)
from recipes.models import (Favorite, Ingredient, IngredientsAmountInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.serializers import RecipeSerializerForSubscriptions


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления ингредиентами - объектами модели Ingredient."""

    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления тэгами - объектами модели Tag."""

    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления рецептами - объектами модели Recipe."""

    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = (IsOwnerAdminOrReadOnlyPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = ApiPagination

    def get_serializer_class(self):
        """
        Выбор сериализатора для разных запросов:
        RecipeGetSerializer для запросов GET, HEAD, OPTIONS ,
        RecipeWriteSerializer для запросов POST, PUT, PATCH, DELETE.
        """
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeWriteSerializer

    def _get_absolute_url(self, recipe):
        return f'/recipes/{self.get_object()}'

    @action(methods=('get',), detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        full_url = request.build_absolute_uri(self._get_absolute_url(recipe))
        short_url = pyshorteners.Shortener().clckru.short(full_url)
        return Response({'short-link': short_url})

    def _write_favorite_and_in_shopping_cart(
            self, request, model,
            success_add_message, success_remove_message
    ):
        """
        Базовый метод для добавления (удаления)
        рецептов в избранное и список покупок.
        """
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт ранее уже добавлен!'},
                    status=HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializerForSubscriptions(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        if request.method == 'DELETE':
            instance = model.objects.filter(user=user, recipe=recipe)
            if not instance.exists():
                return Response(
                    {'errors': 'Данного рецепта нет!'},
                    status=HTTP_400_BAD_REQUEST
                )
            instance.delete()
            return Response(
                {'detail': success_remove_message},
                status=HTTP_204_NO_CONTENT
            )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """Добавление (удаление) рецепта в избранное."""
        return self._write_favorite_and_in_shopping_cart(
            request,
            Favorite,
            'Рецепт успешно добавлен в избранное!',
            'Рецепт успешно удален из избранного!'
        )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """Добавление (удаление) рецепта в список покупок."""
        return self._write_favorite_and_in_shopping_cart(
            request,
            ShoppingCart,
            'Рецепт успешно добавлен в список покупок!',
            'Рецепт успешно удален из списка покупок!'
        )

    @action(
        methods=('get', ),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок в формате txt."""
        ingredients = IngredientsAmountInRecipe.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).order_by(
            'ingredients__name'
        ).annotate(ingredient_total=Sum('amount'))
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = ('attachment;',
                                           'filename="shopping_cart.txt"')
        response.write('Список покупок\n')
        for ingredient in ingredients:
            abb = ingredient['ingredients__measurement_unit__abbreviation']
            response.write(
                f"{ingredient['ingredients__name']}: "
                f"{ingredient['ingredient_total']} " + abb + "\n")
        return response
