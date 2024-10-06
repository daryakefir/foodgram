from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from core.serializers import Base64ImageField
from recipes.models import (
    Favorite, Ingredient, MeasurementUnit,
    ShoppingCart, Tag, Recipe, IngredientsAmountInRecipe, User
)
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Класс сериализатора для работы с ингредиентами."""

    measurement_unit = serializers.CharField(source='measurement_unit.abbreviation')

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        read_only_fields = '__all__',


class TagSerializer(serializers.ModelSerializer):
    """Класс сериализатора для работы с тэгами рецептов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )
        read_only_fields = '__all__',


class IngredientsAmountInRecipeSerializer(serializers.ModelSerializer):
    """Класс сериализатора для корректного отображения количества ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit.abbreviation')

    class Meta:
        model = IngredientsAmountInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        read_only_fields = ('id', 'name', 'measurement_unit')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredient_data = IngredientSerializer(instance.ingredients).data
        representation.update(ingredient_data)
        return representation


class RecipeGetSerializer(serializers.ModelSerializer):
    """
    Класс сериализатора для корректного отображения рецептов
    при запросах GET, HEAD, OPTIONS.
    """

    author = UserSerializer()
    ingredients = IngredientsAmountInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredients_in_recipe'
    )
    tags = TagSerializer(
        many=True,
        read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe
        read_only_fields = '__all__',

    def _in_list(self, obj, model):
        """Базовый метод для отображения, находится ли рецепт в избранном и списке покупок."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self._in_list(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._in_list(obj, ShoppingCart)


class AddIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Класс сериализатора для добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsAmountInRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Класс сериализатора для корректного отображения рецептов
    при запросах POST, PUT, PATCH, DELETE.
    """

    ingredients = AddIngredientsInRecipeSerializer(
        many=True,
        write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    image = Base64ImageField()
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )
        read_only_fields = ('author', )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipe_data = RecipeGetSerializer(instance, context=self.context).data
        representation.update(recipe_data)
        return representation

    def validate_ingredients(self, value):
        """Проверка корректности введенных ингредиентов."""
        ingredients = value
        if not ingredients:
            raise ValidationError(
                {'errors': 'Выберите ингредиенты!!!'})
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, name=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    {'errors': 'Ингредиенты дублируются!!!'})
            if int(item['amount']) <= 1:
               raise ValidationError(
                {'errors': 'Количество ингредиентов не может быть меньше 1!!!'})
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        """Проверка корректности указанных тэгов."""
        tags = value
        if not tags:
            raise ValidationError(
                {'errors': 'Выберите теги!!!'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {'errors': 'Теги дублируются!!!'})
            tags_list.append(tag)
        return value

    def _add_tags_ingredients(self, ingredients, tags, model):
        for ingredient in ingredients:
            IngredientsAmountInRecipe.objects.update_or_create(
                recipe=model,
                ingredients=ingredient['id'],
                amount=ingredient['amount'])
        model.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self._add_tags_ingredients(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self._add_tags_ingredients(ingredients, tags, instance)
        return super().update(instance, validated_data)
