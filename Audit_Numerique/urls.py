from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = routers.DefaultRouter()
router.register(r'utilisateurs', views.UtilisateurViewSet, basename='utilisateur')
router.register(r'cooperatives', views.CooperativeViewSet, basename='cooperative')
router.register(r'membres', views.MembreViewSet, basename='membre')
router.register(r'cotisations', views.CotisationViewSet, basename='cotisation')
router.register(r'prets', views.PretViewSet, basename='pret')                # ← nouveaux
router.register(r'remboursements', views.RemboursementViewSet, basename='remboursement')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'notifications', views.NotificationViewSet, basename='notification')


# Définir un schéma pour Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="Audit Numerique API",
      default_version='v1',
      description="Documentation de l'API pour le projet Audit Numerique",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@auditnumerique.local"),
      license=openapi.License(name="Licence Apache 2.0"),
   ),
   public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("chat/", views.chat, name="chat"),  # API de chat
]
