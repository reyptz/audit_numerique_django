from django.contrib import admin
from .models import (
    Utilisateur, Cooperative, Membre, Cotisation,
    Pret, Remboursement, Transaction, Message, 
    Notification, Audit, Evenement
)

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'actif')
    list_filter = ('role', 'actif', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'telephone')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined', 'date_inscription')}),
    )

@admin.register(Cooperative)
class CooperativeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation', 'admin')
    list_filter = ('date_creation',)
    search_fields = ('nom', 'description')

@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'cooperative', 'date_adhesion', 'actif')
    list_filter = ('cooperative', 'actif', 'date_adhesion')
    search_fields = ('utilisateur__username', 'utilisateur__email', 'cooperative__nom')

@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ('membre', 'montant', 'date_paiement', 'type', 'statut')
    list_filter = ('type', 'statut', 'date_paiement')
    search_fields = ('membre__utilisateur__username', 'membre__cooperative__nom')

@admin.register(Pret)
class PretAdmin(admin.ModelAdmin):
    list_display = ('membre', 'montant', 'taux_interet', 'date_demande', 'date_echeance', 'statut')
    list_filter = ('statut', 'date_demande', 'date_echeance')
    search_fields = ('membre__utilisateur__username', 'motif')

@admin.register(Remboursement)
class RemboursementAdmin(admin.ModelAdmin):
    list_display = ('pret', 'montant', 'date_paiement', 'methode_paiement')
    list_filter = ('methode_paiement', 'date_paiement')
    search_fields = ('pret__membre__utilisateur__username',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'montant', 'date_transaction', 'membre', 'reference')
    list_filter = ('type', 'date_transaction')
    search_fields = ('membre__utilisateur__username', 'description', 'reference')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('expediteur', 'destinataire', 'date_envoi', 'lu')
    list_filter = ('lu', 'date_envoi')
    search_fields = ('expediteur__username', 'destinataire__username', 'contenu')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'type', 'date_creation', 'lue')
    list_filter = ('type', 'lue', 'date_creation')
    search_fields = ('utilisateur__username', 'contenu')

@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('type', 'description', 'date_creation', 'utilisateur')
    list_filter = ('type', 'date_creation')
    search_fields = ('description', 'utilisateur__username')

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'date_debut', 'date_fin', 'cooperative')
    list_filter = ('date_debut', 'date_fin', 'cooperative')
    search_fields = ('titre', 'description', 'cooperative__nom')
