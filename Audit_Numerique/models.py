from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Utilisateur(AbstractUser):
    """
        Utilisateur unique + rôle simplifié (choices).
        Admin ↔ is_staff / is_superuser.
        """
    # rôle applicatif
    ROLE_CHOICES = [
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('tresorier', 'Trésorier'),
        ('secretaire', 'Secrétaire'),
        ('membre', 'Membre'),
    ]
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default='membre')

    telephone        = models.CharField(max_length=20, blank=True, null=True)
    date_inscription = models.DateTimeField(default=timezone.now)
    actif            = models.BooleanField(default=True)

    groups = None
    user_permissions = None

    def __str__(self):
        return f"{self.username}"


class Cooperative(models.Model):
    """Informations sur les coopératives enregistrées"""
    nom = models.CharField(max_length=100)
    description = models.TextField()
    date_creation = models.DateField(auto_now_add=True)
    admin = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True,
                              related_name='cooperatives_administrees')

    def __str__(self):
        return self.nom


class Membre(models.Model):
    """Association entre utilisateurs et coopératives"""
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='adhesions')
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name='membres')
    date_adhesion = models.DateField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        unique_together = ('utilisateur', 'cooperative')

    def __str__(self):
        return f"{self.utilisateur} - {self.cooperative}"


class Cotisation(models.Model):
    """Enregistre les cotisations des membres"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('rejetee', 'Rejetée'),
    ]

    TYPE_CHOICES = [
        ('reguliere', 'Régulière'),
        ('exceptionnelle', 'Exceptionnelle'),
        ('solidarite', 'Solidarité'),
    ]

    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='cotisations')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='reguliere')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"Cotisation de {self.membre.utilisateur} - {self.montant} ({self.date_paiement.strftime('%d/%m/%Y')})"


class Pret(models.Model):
    """Gère les prêts accordés aux membres"""
    STATUT_CHOICES = [
        ('demande', 'Demandé'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
        ('en_cours', 'En cours'),
        ('rembourse', 'Remboursé'),
        ('en_retard', 'En retard'),
    ]

    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='prets')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    taux_interet = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date_demande = models.DateTimeField(default=timezone.now)
    date_approbation = models.DateTimeField(null=True, blank=True)
    date_echeance = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='demande')
    motif = models.TextField()

    def __str__(self):
        return f"Prêt de {self.montant} à {self.membre.utilisateur} ({self.statut})"


class Remboursement(models.Model):
    """Suivi des remboursements de prêts"""
    METHODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('mobile_money', 'Mobile Money'),
        ('virement', 'Virement bancaire'),
        ('autre', 'Autre'),
    ]

    pret = models.ForeignKey(Pret, on_delete=models.CASCADE, related_name='remboursements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(default=timezone.now)
    methode_paiement = models.CharField(max_length=20, choices=METHODE_PAIEMENT_CHOICES, default='especes')

    def __str__(self):
        return f"Remboursement de {self.montant} pour prêt #{self.pret.id}"


class Transaction(models.Model):
    """Historique de toutes les transactions financières"""
    TYPE_CHOICES = [
        ('cotisation', 'Cotisation'),
        ('pret', 'Prêt'),
        ('remboursement', 'Remboursement'),
        ('autre', 'Autre'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_transaction = models.DateTimeField(default=timezone.now)
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='transactions')
    description = models.TextField()
    reference = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.type} - {self.montant} ({self.date_transaction.strftime('%d/%m/%Y')})"


class Message(models.Model):
    """Système de messagerie interne"""
    expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_recus')
    contenu = models.TextField()
    date_envoi = models.DateTimeField(default=timezone.now)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Message de {self.expediteur} à {self.destinataire} ({self.date_envoi.strftime('%d/%m/%Y')})"


class Notification(models.Model):
    """Gestion des notifications système"""
    TYPE_CHOICES = [
        ('cotisation', 'Cotisation'),
        ('pret', 'Prêt'),
        ('remboursement', 'Remboursement'),
        ('systeme', 'Système'),
        ('autre', 'Autre'),
    ]

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contenu = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    lue = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification {self.type} pour {self.utilisateur} ({self.date_creation.strftime('%d/%m/%Y')})"


class Audit(models.Model):
    """Enregistrement des activités d'audit"""
    TYPE_CHOICES = [
        ('financier', 'Financier'),
        ('securite', 'Sécurité'),
        ('systeme', 'Système'),
        ('utilisateur', 'Utilisateur'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    details = models.JSONField(default=dict)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='audits')

    def __str__(self):
        return f"Audit {self.type} - {self.date_creation.strftime('%d/%m/%Y')}"


class Evenement(models.Model):
    """Gestion du calendrier des événements"""
    titre = models.CharField(max_length=100)
    description = models.TextField()
    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(default=timezone.now)
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name='evenements')

    def __str__(self):
        return f"{self.titre} ({self.date_debut.strftime('%d/%m/%Y')})"