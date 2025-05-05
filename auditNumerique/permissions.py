from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre aux administrateurs de modifier,
    mais autoriser uniquement la lecture pour les autres utilisateurs.
    """
    def has_permission(self, request, view):
        # Autoriser les méthodes GET, HEAD, OPTIONS pour tous les utilisateurs
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Autoriser les modifications uniquement pour les administrateurs
        return request.user and (request.user.is_staff or request.user.is_superuser)

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée pour permettre aux propriétaires d'un objet ou aux administrateurs
    d'accéder ou de modifier cet objet.
    """
    def has_object_permission(self, request, view, obj):
        # Vérifier si l'utilisateur est administrateur
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Vérifier si l'utilisateur est le propriétaire
        if hasattr(obj, 'utilisateur'):
            return obj.utilisateur == request.user
        elif hasattr(obj, 'expediteur'):
            return obj.expediteur == request.user
        elif hasattr(obj, 'destinataire') and request.method in permissions.SAFE_METHODS:
            return obj.destinataire == request.user
        
        return False

class IsTresorier(permissions.BasePermission):
    """
    Permission personnalisée pour les trésoriers.
    """
    def has_permission(self, request, view):
        # Vérifier si l'utilisateur est connecté et a le rôle de trésorier
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        if request.user.role and hasattr(request.user.role, 'nom'):
            return request.user.role.nom.lower() == 'trésorier'
        
        return False

class IsSecretaire(permissions.BasePermission):
    """
    Permission personnalisée pour les secrétaires.
    """
    def has_permission(self, request, view):
        # Vérifier si l'utilisateur est connecté et a le rôle de secrétaire
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        if request.user.role and hasattr(request.user.role, 'nom'):
            return request.user.role.nom.lower() == 'secrétaire'
        
        return False
