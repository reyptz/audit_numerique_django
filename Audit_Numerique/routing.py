from django.urls import re_path
from .views import AuditConsumer

websocket_urlpatterns = [
    re_path(r'^ws/$', AuditConsumer.as_asgi()),
]