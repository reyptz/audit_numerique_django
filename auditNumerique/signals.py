from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pret, Remboursement, Notification, Cotisation, Transaction, Role
from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model


@receiver(post_migrate)
def create_admin_user(sender, app_config, **kwargs):
    if app_config.name == 'auditNumerique':
        User = get_user_model()
        try:
            admin_role = Role.objects.get(nom='admin')
        except Role.DoesNotExist:
            admin_role = Role.objects.create(nom='admin', description='Rôle administrateur')

        if not User.objects.filter(username='superadmin').exists():
            superadmin = User.objects.create_superuser(
                username='superadmin',
                email='admin@example.com',
                password='motdepasse123'  # Remplacez par un mot de passe réel
            )
            superadmin.role = admin_role
            superadmin.is_staff = True
            superadmin.is_superuser = True
            superadmin.save()
            print("Superutilisateur 'superadmin' créé avec le rôle 'admin'.")
        else:
            print("Le superutilisateur 'superadmin' existe déjà.")


@receiver(post_save, sender=Pret)
def create_pret_notification(sender, instance, created, **kwargs):
    """Crée une notification lorsqu'un prêt est créé ou son statut change"""
    if created:
        # Notification pour l'administrateur
        if instance.membre.cooperative.admin:
            Notification.objects.create(
                utilisateur=instance.membre.cooperative.admin,
                type='pret',
                contenu=f"Nouvelle demande de prêt de {instance.membre.utilisateur.get_full_name()} pour {instance.montant}."
            )
    else:
        # Notification pour le membre si le statut a changé
        if instance.statut in ['approuve', 'rejete']:
            Notification.objects.create(
                utilisateur=instance.membre.utilisateur,
                type='pret',
                contenu=f"Votre demande de prêt de {instance.montant} a été {instance.get_statut_display().lower()}."
            )

@receiver(post_save, sender=Remboursement)
def update_pret_status(sender, instance, created, **kwargs):
    """Met à jour le statut du prêt lorsqu'un remboursement est effectué"""
    if created:
        pret = instance.pret
        total_rembourse = sum(r.montant for r in pret.remboursements.all())
        
        if total_rembourse >= pret.montant:
            pret.statut = 'rembourse'
            pret.save()
            
            # Notification pour le membre
            Notification.objects.create(
                utilisateur=pret.membre.utilisateur,
                type='remboursement',
                contenu=f"Votre prêt de {pret.montant} a été entièrement remboursé."
            )

@receiver(post_save, sender=Cotisation)
def create_cotisation_transaction(sender, instance, created, **kwargs):
    """Crée une transaction lorsqu'une cotisation est validée"""
    if not created and instance.statut == 'validee':
        # Vérifier si une transaction existe déjà pour cette cotisation
        if not Transaction.objects.filter(reference=f"COT-{instance.id}").exists():
            Transaction.objects.create(
                type='cotisation',
                montant=instance.montant,
                membre=instance.membre,
                description=f"Cotisation {instance.get_type_display()}",
                reference=f"COT-{instance.id}"
            )
