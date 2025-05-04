from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    Role, Utilisateur, Cooperative, Membre, Cotisation,
    Pret, Remboursement, Transaction, Message,
    Notification, Audit, Evenement
)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'telephone', 'date_inscription', 'role', 'is_staff', 'is_active')
        read_only_fields = ('id', 'date_inscription')

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Utilisateur
        fields = ('username', 'first_name', 'last_name', 'email', 'telephone', 'password')

    def create(self, validated_data):
        user = Utilisateur.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            telephone=validated_data['telephone'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

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