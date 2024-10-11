from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes.constants import (
    LENGTH_ABB_MEASUREMENT_UNIT, LENGTH_NAME_INGREDIENT,
    LENGTH_NAME_MEASUREMENT_UNIT, LENGTH_NAME_RECIPE, LENGTH_NAME_TAG,
    MAX_COOKING_TIME, MAX_DISPLAY_LENGTH,
    MAX_INGRDEINTS_AMOUNT,
    MIN_COOKING_TIME, MIN_INGRDEINTS_AMOUNT
)
from users.models import User


class MeasurementUnit(models.Model):
    """Модель, описывающая единицы измерения."""

    name = models.CharField(
        max_length=LENGTH_NAME_MEASUREMENT_UNIT,
        unique=True,
        verbose_name='Название'
    )
    abbreviation = models.CharField(
        max_length=LENGTH_ABB_MEASUREMENT_UNIT,
        unique=True,
        verbose_name='Сокращенное название'
    )

    class Meta:
        ordering = ('name',)
        default_related_name = 'measurement_units'
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.name[:MAX_DISPLAY_LENGTH]


class Ingredient(models.Model):
    """Модель, описывающая ингредиенты."""

    name = models.CharField(
        max_length=LENGTH_NAME_INGREDIENT,
        verbose_name='Название',
        unique=True
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ingredients',
    )

    class Meta:
        default_related_name = 'ingredients'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_DISPLAY_LENGTH]


class Tag(models.Model):
    """Модель, описывающая тэги для рецептов."""

    name = models.CharField(
        max_length=LENGTH_NAME_TAG,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        default_related_name = 'tags'
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_DISPLAY_LENGTH]


class Recipe(models.Model):
    """Модель, описываюшая рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=LENGTH_NAME_RECIPE,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        verbose_name='Изображение',
        default=None
    )
    text = models.TextField(verbose_name='Текст рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientsAmountInRecipe'
    )
    tags = models.ManyToManyField(
        Tag
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Минимальное время готовки:{MIN_COOKING_TIME}'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Максимальное время готовки:{MAX_COOKING_TIME}'
            )
        ),
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return f'{self.name} from {self.author}'[:MAX_DISPLAY_LENGTH]


class IngredientsAmountInRecipe(models.Model):
    """Промежуточная модель для связи Recipe и Ingredient."""

    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_INGRDEINTS_AMOUNT,
                message=f'Минимальное количество ингредиентов:'
                        f'{MIN_INGRDEINTS_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_INGRDEINTS_AMOUNT,
                message=f'Максимальное количество ингредиентов:'
                        f'{MAX_INGRDEINTS_AMOUNT}'
            )
        ),
    )

    class Meta:
        verbose_name = 'Количество ингредиентов в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredients', 'recipe'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.ingredients} {self.amount}'[:MAX_DISPLAY_LENGTH]


class Favorite(models.Model):
    """Модель, описывающая параметры добавления рецептов в избранное."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('user',)
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f'{self.recipe} in favorites {self.user}'[:MAX_DISPLAY_LENGTH]


class ShoppingCart(models.Model):
    """Модель, описывающая параметры добавления рецептов в список покупок."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        default_related_name = 'shoppingcart'
        ordering = ('user',)
        unique_together = ('recipe', 'user')

    def __str__(self):
        return (f'{self.recipe} '
                f'in shopping cart '
                f'{self.user}')[:MAX_DISPLAY_LENGTH]
