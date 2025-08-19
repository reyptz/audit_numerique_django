from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    Utilisateur, Cooperative, Membre, Cotisation,
    Pret, Remboursement, Transaction, Message,
    Notification, Audit, Evenement
)

User = Utilisateur()

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = (
            "id", "username", "first_name", "last_name", "email",
            "telephone", "role", "date_inscription", "is_staff", "is_active"
        )
        read_only_fields = ("id", "date_inscription", "is_staff")

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = Utilisateur
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "telephone",
            "role",
            "password",
        )

    def validate_username(self, v):
        if Utilisateur.objects.filter(username=v).exists():
            raise serializers.ValidationError("Nom d’utilisateur déjà pris.")
        return v

    def create(self, data):
        return Utilisateur.objects.create_user(
            username=data["username"],
            password=data["password"],
            email    = data.get("email", ""),
            first_name = data.get("first_name", ""),
            last_name  = data.get("last_name", ""),
            telephone  = data.get("telephone", ""),
            role       = data.get("role", "membre"),
        )

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Identifiants invalides")
        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé")
        data["user"] = user
        return data

class CooperativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooperative
        fields = '__all__'
        read_only_fields = ['id', 'date_creation']

class MembreSerializer(serializers.ModelSerializer):
    utilisateur = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(), write_only=True
    )
    cooperative = serializers.PrimaryKeyRelatedField(
        queryset=Cooperative.objects.all(), write_only=True
    )
    utilisateur_detail = UtilisateurSerializer(source='utilisateur', read_only=True)
    cooperative_detail = CooperativeSerializer(source='cooperative', read_only=True)

    class Meta:
        model = Membre
        fields = ['id', 'utilisateur', 'cooperative', 'date_adhesion', 'actif', 'utilisateur_detail', 'cooperative_detail']
        read_only_fields = ('date_adhesion', 'utilisateur_detail', 'cooperative_detail')

    def validate(self, data):
        utilisateur = data.get('utilisateur')
        cooperative = data.get('cooperative')

        # Check for unique_together constraint
        if Membre.objects.filter(utilisateur=utilisateur, cooperative=cooperative).exists():
            raise serializers.ValidationError({
                "non_field_errors": "Ce membre est déjà associé à cette coopérative."
            })

        return data

class CotisationSerializer(serializers.ModelSerializer):
    membre = serializers.PrimaryKeyRelatedField(
        queryset=Membre.objects.all(), write_only=True
    )
    membre_detail = MembreSerializer(source='membre', read_only=True)

    class Meta:
        model = Cotisation
        fields = ['id', 'membre', 'membre_detail', 'montant', 'date_paiement', 'type', 'statut']
        read_only_fields = ('date_paiement', 'membre_detail')

    def validate(self, data):
        # Optional: Add custom validation if needed
        membre = data.get('membre')
        if not membre:
            raise serializers.ValidationError({"membre": "Le membre est requis."})
        return data

class PretSerializer(serializers.ModelSerializer):
    membre = serializers.PrimaryKeyRelatedField(queryset=Membre.objects.all())
    # si tu veux le détail en lecture:
    membre_detail = MembreSerializer(source="membre", read_only=True)

    class Meta:
        model  = Pret
        fields = '__all__'
        read_only_fields = ('date_demande', 'date_approbation')

class RemboursementSerializer(serializers.ModelSerializer):
    pret = serializers.PrimaryKeyRelatedField(queryset=Pret.objects.all())
    pret_detail = PretSerializer(source="pret", read_only=True)

    class Meta:
        model  = Remboursement
        fields = '__all__'
        read_only_fields = ('date_paiement',)

class TransactionSerializer(serializers.ModelSerializer):
    membre = serializers.PrimaryKeyRelatedField(queryset=Membre.objects.all())
    membre_detail = MembreSerializer(source="membre", read_only=True)

    class Meta:
        model  = Transaction
        fields = '__all__'
        read_only_fields = ('date_transaction',)

class MessageSerializer(serializers.ModelSerializer):
    expediteur = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(), required=False
    )
    destinataire = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.all())
    expediteur_detail = UtilisateurSerializer(source="expediteur", read_only=True)
    destinataire_detail = UtilisateurSerializer(source="destinataire", read_only=True)

    class Meta:
        model  = Message
        fields = '__all__'
        read_only_fields = ('date_envoi',)

class NotificationSerializer(serializers.ModelSerializer):
    utilisateur = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(), required=False
    )
    utilisateur_detail = UtilisateurSerializer(source="utilisateur", read_only=True)

    class Meta:
        model  = Notification
        fields = '__all__'
        read_only_fields = ('date_creation',)

class AuditSerializer(serializers.ModelSerializer):
    utilisateur = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(), required=False
    )
    utilisateur_detail = UtilisateurSerializer(source="utilisateur", read_only=True)

    class Meta:
        model  = Audit
        fields = '__all__'
        read_only_fields = ('date_creation',)

class EvenementSerializer(serializers.ModelSerializer):
    cooperative = serializers.PrimaryKeyRelatedField(queryset=Cooperative.objects.all())
    cooperative_detail = CooperativeSerializer(source="cooperative", read_only=True)

    class Meta:
        model  = Evenement
        fields = '__all__'