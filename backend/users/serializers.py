from rest_framework import serializers
from rest_framework.response import Response

from core.serializers import Base64ImageField
from recipes.models import Recipe
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Класс сериализатора для работы с пользователями."""

    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def create(self, validated_data):
        """Переопределение метода создания пользователя."""
        new_user = User.objects.create_user(**validated_data)
        return Response(
            {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name
            }
        )

    def get_is_subscribed(self, obj):
        """
        Проверка, подписан ли текущий авторизованный пользователь
        на выбранного пользователя.
        """
        user = self.context['request'].user
        if not user.is_anonymous:
            return user.subscribers.filter(following=obj).exists()
        return False


class RecipeSerializerForSubscriptions(serializers.ModelSerializer):
    """Класс сериализатора для вывода рецептов в подписках."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = '__all__',


class FollowSerializer(serializers.ModelSerializer):
    """Класс сериализатора для работы с подписками и подписчиками."""

    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    email = serializers.ReadOnlyField(source='following.email')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    avatar = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        """Получение ссылки на аватар."""
        user = obj.following if hasattr(obj, 'following') else obj['following']
        return user.avatar.url if user.avatar else None

    def get_recipes_count(self, obj):
        """
        Получение количества рецептов,
        автором которого является выбранный пользователь.
        """
        user = obj if hasattr(obj, 'following') else obj['following']
        return Recipe.objects.filter(author=user.id).count()

    def get_recipes(self, obj):
        """
        Получение списка рецептов,
        автором которого является выбранный пользователь.
        """
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        user = obj if hasattr(obj, 'following') else obj['following']
        recipes = Recipe.objects.filter(author=user.id)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeSerializerForSubscriptions(recipes, many=True).data

    def get_is_subscribed(self, obj):
        """
        Проверка, подписан ли текущий авторизованный пользователь
        на выбранного пользователя.
        """
        user = self.context['request'].user
        following = obj.following if hasattr(obj, 'following') \
            else obj['following']
        if not user.is_anonymous:
            return user.subscribers.filter(following=following).exists()
        return False

    class Meta:
        model = Follow
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'recipes',
            'recipes_count',
            'is_subscribed'
        )


class FollowCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Follow
        fields = (
            'user',
            'following',
        )
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на данного пользователя!!!'
            ),
        )

    def validate_following(self, obj):
        """
        Проверка, является ли выбранный для подписки пользователь
        текущим авторизованным пользователем.
        """
        if self.context['request'].user == obj:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя!!!'}
            )
        return obj

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('user', None)
        representation.pop('following', None)
        user_data = FollowSerializer(instance, context=self.context).data
        representation.update(user_data)
        return representation
