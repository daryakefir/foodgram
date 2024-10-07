from django.contrib import admin

from users.models import User


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
