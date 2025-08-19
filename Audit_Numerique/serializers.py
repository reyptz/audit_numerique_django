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
        read_only_fields = ('date_creation',)

class MembreSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(read_only=True) # Or use PrimaryKeyRelatedField if you prefer
    cooperative = CooperativeSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Membre
        fields = '__all__'
        read_only_fields = ('date_adhesion',)

class CotisationSerializer(serializers.ModelSerializer):
    membre = MembreSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Cotisation
        fields = '__all__'
        read_only_fields = ('date_paiement',)

class PretSerializer(serializers.ModelSerializer):
    membre = MembreSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Pret
        fields = '__all__'
        read_only_fields = ('date_demande', 'date_approbation')

class RemboursementSerializer(serializers.ModelSerializer):
    pret = PretSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Remboursement
        fields = '__all__'
        read_only_fields = ('date_paiement',)

class TransactionSerializer(serializers.ModelSerializer):
    membre = MembreSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('date_transaction',)

class MessageSerializer(serializers.ModelSerializer):
    expediteur = UtilisateurSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    destinataire = UtilisateurSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('date_envoi',)

class NotificationSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('date_creation',)

class AuditSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Audit
        fields = '__all__'
        read_only_fields = ('date_creation',)

class EvenementSerializer(serializers.ModelSerializer):
    cooperative = CooperativeSerializer(read_only=True) # Or use PrimaryKeyRelatedField
    class Meta:
        model = Evenement
        fields = '__all__'