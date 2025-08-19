# permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, req, view):
        return req.user and req.user.is_staff

class IsTresorier(BasePermission):
    def has_permission(self, req, view):
        return req.user.is_authenticated and req.user.role == 'tresorier'

class IsSecretaire(BasePermission):
    def has_permission(self, req, view):
        return req.user.is_authenticated and req.user.role == 'secretaire'

class ReadOnly(BasePermission):
    def has_permission(self, req, view):
        return req.method in SAFE_METHODS
