from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('api.urls',)),
    path('', include('users.urls',)),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
