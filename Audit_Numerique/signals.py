# Audit_Numerique/signals.py
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Pret, Remboursement, Notification, Cotisation, Transaction

User = get_user_model()

# ---------- Création auto du superadmin ----------
@receiver(post_migrate)
def create_superadmin(sender, app_config, **kwargs):
    """Crée un superutilisateur 'superadmin' s’il n’existe pas déjà."""
    if app_config.name != "Audit_Numerique":
        return

    if not User.objects.filter(username="superadmin").exists():
        User.objects.create_superuser(
            username="superadmin",
            email="admin@example.com",
            password="6/u_Nf:4(63\Ib#]",      # ← mets un vrai mot de passe
            role="superadmin",                # ou "tresorier" / "secretaire"
        )
        print("✅ Superutilisateur 'superadmin' créé.")
    else:
        print("ℹ️  Le superutilisateur 'superadmin' existe déjà.")


# ---------- Notifications & transactions ----------
@receiver(post_save, sender=Pret)
def pret_notifications(sender, instance, created, **kwargs):
    if created and instance.membre.cooperative.admin:
        Notification.objects.create(
            utilisateur=instance.membre.cooperative.admin,
            type="pret",
            contenu=f"Nouvelle demande de prêt de {instance.membre.utilisateur.get_full_name()} pour {instance.montant}."
        )
    elif not created and instance.statut in ["approuve", "rejete"]:
        Notification.objects.create(
            utilisateur=instance.membre.utilisateur,
            type="pret",
            contenu=f"Votre demande de prêt de {instance.montant} a été {instance.get_statut_display().lower()}."
        )


@receiver(post_save, sender=Remboursement)
def update_pret_status(sender, instance, created, **kwargs):
    if not created:
        return
    pret = instance.pret
    total = pret.remboursements.aggregate(somme=Pret.Sum("montant"))["somme"] or 0
    if total >= pret.montant:
        pret.statut = "rembourse"
        pret.save()
        Notification.objects.create(
            utilisateur=pret.membre.utilisateur,
            type="remboursement",
            contenu=f"Votre prêt de {pret.montant} est désormais remboursé."
        )


@receiver(post_save, sender=Cotisation)
def cotisation_transaction(sender, instance, created, **kwargs):
    if created or instance.statut != "validee":
        return
    ref = f"COT-{instance.id}"
    if not Transaction.objects.filter(reference=ref).exists():
        Transaction.objects.create(
            type="cotisation",
            montant=instance.montant,
            membre=instance.membre,
            description=f"Cotisation {instance.get_type_display()}",
            reference=ref,
        )
