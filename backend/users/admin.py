from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс для настройки админ-зоны модели User."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
        'role',
        'admin'
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class UserAdmin(admin.ModelAdmin):
    """Класс для настройки админ-зоны модели Follow."""

    list_display = (
        'user',
        'following'
    )
    search_fields = ('user', 'following')
    list_filter = ('user', 'following')
    empty_value_display = '-пусто-'
