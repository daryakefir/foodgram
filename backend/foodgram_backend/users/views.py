from djoser.views import UserViewSet
from django.contrib.auth import update_session_auth_hash
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
)

from core.paginations import ApiPagination
from core.permissions import IsOwnerAdminOrReadOnlyPermission
from users.models import Follow, User
from users.serializers import FollowSerializer, UserSerializer


class FoodgramUserViewSet(UserViewSet):
    """
    Вьюсет для управления пользователями и его подписками
    - объектами модели User и Follow.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = ApiPagination
    permission_classes = (IsOwnerAdminOrReadOnlyPermission,)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Возвращает данные текущего аутентифицированного пользователя."""
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=('get', 'put', 'delete'),
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request):
        """Управление аватаром текущего пользователя."""
        user = self.request.user
        if request.method == 'GET':
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)
        elif request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {'errors': 'Поле аватара должно быть заполнено.'},
                    status=HTTP_400_BAD_REQUEST
                )
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'avatar': serializer.data['avatar']}
                )
            return Response(
                {'errors:'},
                status=HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            user.avatar.delete()
            user.save()
            return Response(
                {'detail': 'Аватар успешно обновлен!'},
                status=HTTP_204_NO_CONTENT
            )

    @action(
        methods=('post',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        """Обновляет пароль текущего пользователя."""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not current_password or not new_password:
            return Response(
                {'errors': 'Необходимо ввести пароли!!!'},
                status=HTTP_400_BAD_REQUEST
            )
        if not user.check_password(current_password):
            return Response(
                {'errors': 'Введенный текущий пароль некорректный!!!'},
                status=HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response(
            {'detail': 'Пароль успешно обновлен!'},
            status=HTTP_204_NO_CONTENT
        )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Подписка/отписка на пользователя."""
        user = request.user
        following = self.get_object()
        if user == following:
            return Response(
                {'errors': 'Нельзя подписаться на себя!!!'},
                status=HTTP_400_BAD_REQUEST
            )
        if request.method == 'POST':
            if Follow.objects.filter(user=user, following=following).exists():
                return Response(
                    {'errors': 'Вы уже подписаны!!!'},
                    status=HTTP_400_BAD_REQUEST
                )
            subscription = Follow.objects.create(
                user=user,
                following=following
            )
            serializer = FollowSerializer(
                subscription,
                context={'request': request}
            )
            return Response(serializer.data, status=HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscribtion = Follow.objects.filter(
                user=user,
                following=following
            )
            if not subscribtion.exists():
                return Response(
                    {'errors': f'Вы не подписаны на {following}!'},
                    status=HTTP_400_BAD_REQUEST
                )
            subscribtion.delete()
            return Response(
                {'detail': f'Вы успешно отписались от {following}!'},
                status=HTTP_204_NO_CONTENT
            )

    @action(
        methods=('get',),
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        """Получает подписки текущего пользователя."""
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
