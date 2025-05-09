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
router.register(r'roles', views.RoleViewSet)
router.register(r'utilisateurs', views.UtilisateurViewSet)
router.register(r'cooperatives', views.CooperativeViewSet) # Enregistrez le nouveau ViewSet
router.register(r'membres', views.MembreViewSet)       # Enregistrez le nouveau ViewSet
router.register(r'cotisations', views.CotisationViewSet) # Enregistrez le nouveau ViewSet


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
    # path('api/', include('Audit_Numerique.urls')),  # Inclure les routes de ton app
    # Ajouter Swagger à l'URL
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Obtient une paire de tokens (access et refresh)
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Obtient un nouveau token d'accès en utilisant un refresh token valide
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),    # Vérifie la validité d'un token d'accès
    path("chat/", views.chat, name="chat"),  # API de chat
]
