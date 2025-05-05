from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Q
from .models import (
    Role, Utilisateur, Cooperative, Membre, Cotisation,
    Pret, Remboursement, Transaction, Message,
    Notification, Audit, Evenement
)
from .serializers import (
    RoleSerializer, UtilisateurSerializer, LoginSerializer,
    CooperativeSerializer, MembreSerializer, CotisationSerializer,
    PretSerializer, RemboursementSerializer, TransactionSerializer,
    MessageSerializer, NotificationSerializer, AuditSerializer,
    EvenementSerializer, RegistrationSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsOwnerOrAdmin, IsTresorier
)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nom']
    search_fields = ['nom', 'description']
    ordering_fields = ['nom']


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    #permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['username', 'email', 'role', 'actif']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telephone']
    ordering_fields = ['username', 'date_inscription']

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UtilisateurSerializer(user).data
        })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UtilisateurSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def me(self, request):
        serializer = UtilisateurSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'error': 'Les deux mots de passe sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(old_password):
            return Response(
                {'error': 'Ancien mot de passe incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({'success': 'Mot de passe changé avec succès'})


class CooperativeViewSet(viewsets.ModelViewSet):
    queryset = Cooperative.objects.all()
    serializer_class = CooperativeSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nom', 'admin']
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'date_creation']

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def membres(self, request, pk=None):
        cooperative = self.get_object()
        membres = Membre.objects.filter(cooperative=cooperative)
        serializer = MembreSerializer(membres, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def evenements(self, request, pk=None):
        cooperative = self.get_object()
        evenements = Evenement.objects.filter(cooperative=cooperative)
        serializer = EvenementSerializer(evenements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def statistiques(self, request, pk=None):
        cooperative = self.get_object()
        nb_membres = Membre.objects.filter(cooperative=cooperative).count()
        nb_membres_actifs = Membre.objects.filter(cooperative=cooperative, actif=True).count()
        total_cotisations = Cotisation.objects.filter(
            membre__cooperative=cooperative,
            statut='validee'
        ).aggregate(total=Sum('montant'))['total'] or 0
        total_prets = Pret.objects.filter(
            membre__cooperative=cooperative,
            statut__in=['approuve', 'en_cours']
        ).aggregate(total=Sum('montant'))['total'] or 0
        total_remboursements = Remboursement.objects.filter(
            pret__membre__cooperative=cooperative
        ).aggregate(total=Sum('montant'))['total'] or 0
        solde = float(total_cotisations) - float(total_prets) + float(total_remboursements)
        return Response({
            'nb_membres': nb_membres,
            'nb_membres_actifs': nb_membres_actifs,
            'total_cotisations': total_cotisations,
            'total_prets': total_prets,
            'total_remboursements': total_remboursements,
            'solde': solde
        })


class MembreViewSet(viewsets.ModelViewSet):
    queryset = Membre.objects.all()
    serializer_class = MembreSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['utilisateur', 'cooperative', 'actif']
    search_fields = ['utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name']
    ordering_fields = ['date_adhesion']

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def cotisations(self, request, pk=None):
        membre = self.get_object()
        cotisations = Cotisation.objects.filter(membre=membre)
        serializer = CotisationSerializer(cotisations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def prets(self, request, pk=None):
        membre = self.get_object()
        prets = Pret.objects.filter(membre=membre)
        serializer = PretSerializer(prets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def transactions(self, request, pk=None):
        membre = self.get_object()
        transactions = Transaction.objects.filter(membre=membre)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class CotisationViewSet(viewsets.ModelViewSet):
    queryset = Cotisation.objects.all()
    serializer_class = CotisationSerializer
    # permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['membre', 'type', 'statut']
    search_fields = ['membre__utilisateur__username', 'type']
    ordering_fields = ['date_paiement', 'montant']