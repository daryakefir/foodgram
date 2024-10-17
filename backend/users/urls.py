from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import FoodgramUserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', FoodgramUserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router_v1.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
