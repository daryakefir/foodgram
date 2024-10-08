from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q

from users.constants import USERNAME_LENGTH
from users.validators import UsernameValidator


class User (AbstractUser):
    """Расширение стандартной модели User."""

    class Roles(models.TextChoices):
        USER = 'user'
        ADMIN = 'admin'

    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        validators=(UsernameValidator(),)
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.TextField(
        verbose_name='Имя',
        max_length=USERNAME_LENGTH
    )
    last_name = models.TextField(
        verbose_name='Фамилия',
        max_length=USERNAME_LENGTH
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        default=None
    )
    role = models.CharField(
        max_length=max(len(role) for role in Roles.values),
        choices=Roles.choices,
        default=Roles.USER,
        verbose_name='Права пользователя'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        default_related_name = 'users'
        ordering = ('id',)

    def __str__(self):
        """Возвращает username в качестве строкового представления объекта."""
        return self.username[:USERNAME_LENGTH]

    @property
    def admin(self):
        """Возвращает поле role со значение ADMIN."""
        return (
                self.role == self.Roles.ADMIN
                or self.is_staff or self.is_superuser
        )


class Follow(models.Model):
    """
    Модель, описывающая параметры
    подписок пользователей на других пользователей.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчики',
        blank=False,
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписки',
        blank=False,
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        default_related_name = 'followers'
        constraints = (
            CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='check_user_cant_follow_himself',
            ),
            CheckConstraint(
                check=~Q(user=F('following')),
                name='no_self_following')
        )

    def __str__(self):
        return f'{self.user} following {self.following}'
