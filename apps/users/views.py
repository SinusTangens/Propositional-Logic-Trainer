from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """SessionAuthentication ohne CSRF-Prüfung für bestimmte Endpunkte."""
    def enforce_csrf(self, request):
        return  # CSRF-Prüfung überspringen

from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    PasswordChangeSerializer,
    AttemptSerializer,
    AvatarSerializer
)
from .models import Attempt, UserProgress

User = get_user_model()


class RegisterView(APIView):
    """Endpoint für die Benutzerregistrierung."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Direkt einloggen nach Registrierung
            login(request, user)
            return Response({
                'message': 'Registrierung erfolgreich',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    """Endpoint für den Login."""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Benutzername und Passwort erforderlich'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                'message': 'Login erfolgreich',
                'user': UserSerializer(user).data
            })
        else:
            return Response(
                {'error': 'Ungültige Anmeldedaten'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """Endpoint für den Logout."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout erfolgreich'})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CurrentUserView(APIView):
    """Endpoint für den aktuellen eingeloggten Nutzer."""
    
    permission_classes = [AllowAny]  # Erlaubt anonyme Anfragen, gibt dann null zurück
    
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'isAuthenticated': True,
                'user': UserSerializer(request.user).data
            })
        return Response({
            'isAuthenticated': False,
            'user': None
        })


class PasswordChangeView(APIView):
    """Endpoint für Passwortänderung."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Das alte Passwort ist falsch'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            # Session aktualisieren damit der User eingeloggt bleibt
            login(request, user)
            return Response({'message': 'Passwort erfolgreich geändert'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetProgressView(APIView):
    """Endpoint zum Zurücksetzen des Fortschritts."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Statistiken zurücksetzen
        user.total_solved = 0
        user.correct_solved = 0
        # highscore_streak bleibt als "All-Time-High"
        user.save()
        
        # Progress zurücksetzen
        UserProgress.objects.filter(user=user).update(
            current_level=1,
            correct_in_row=0,
            is_completed=False
        )
        
        # Attempts löschen
        Attempt.objects.filter(user=user).delete()
        
        return Response({
            'message': 'Fortschritt erfolgreich zurückgesetzt',
            'user': UserSerializer(user).data
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet für Benutzer (nur lesen)."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Gibt den aktuellen eingeloggten Nutzer zurück."""
        return Response(UserSerializer(request.user).data)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateAvatarView(APIView):
    """Endpoint zum Aktualisieren des Avatars."""
    
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        data = request.data
        
        # Erlaubte Avatar-Felder
        avatar_fields = {
            'skinColor': 'avatar_skin_color',
            'hairColor': 'avatar_hair_color',
            'top': 'avatar_top',
            'accessories': 'avatar_accessories',
            'facialHair': 'avatar_facial_hair',
            'clothing': 'avatar_clothing',
            'clothingColor': 'avatar_clothing_color',
            'eyes': 'avatar_eyes',
            'eyebrows': 'avatar_eyebrows',
            'mouth': 'avatar_mouth',
        }
        
        # Nur gültige Felder aktualisieren
        for frontend_key, model_field in avatar_fields.items():
            if frontend_key in data:
                setattr(user, model_field, data[frontend_key])
        
        user.save()
        
        return Response({
            'message': 'Avatar erfolgreich aktualisiert',
            'avatar': {
                'skinColor': user.avatar_skin_color,
                'hairColor': user.avatar_hair_color,
                'top': user.avatar_top,
                'accessories': user.avatar_accessories,
                'facialHair': user.avatar_facial_hair,
                'clothing': user.avatar_clothing,
                'clothingColor': user.avatar_clothing_color,
                'eyes': user.avatar_eyes,
                'eyebrows': user.avatar_eyebrows,
                'mouth': user.avatar_mouth,
                'url': user.get_avatar_url()
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class RandomizeAvatarView(APIView):
    """Endpoint um einen zufälligen Avatar zu generieren."""
    
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        import random
        
        user = request.user
        
        # Zufällige Optionen für jeden Avatar-Aspekt (DiceBear 9.x - Hex-Farben)
        skin_colors = ['ffdbb4', 'edb98a', 'd08b5b', 'ae5d29', '614335', '3c2416']
        hair_colors = ['2c1b18', '4a312c', '724133', 'a55728', 'c93305', 'b58143', 'd6b370', 'ecdcbf']
        tops = [
            # Kurze Haare
            'shortFlat', 'shortCurly', 'shortRound', 'shortWaved', 'sides', 
            'theCaesar', 'theCaesarAndSidePart', 'dreads01', 'dreads02', 'frizzle',
            'shaggy', 'shaggyMullet',
            # Lange Haare  
            'bigHair', 'bob', 'bun', 'curly', 'curvy', 'dreads', 'frida', 'fro', 
            'froBand', 'longButNotTooLong', 'miaWallace', 'shavedSides',
            'straight01', 'straight02', 'straightAndStrand',
            # Kopfbedeckungen
            'hat', 'hijab', 'turban', 'winterHat1', 'winterHat02', 'winterHat03', 'winterHat04'
        ]
        accessories_list = ['', 'kurt', 'prescription01', 'prescription02', 'round', 'sunglasses', 'wayfarers']
        facial_hair_list = ['', 'beardLight', 'beardMajestic', 'beardMedium', 'moustacheFancy', 'moustacheMagnum']
        clothing_list = ['blazerAndShirt', 'blazerAndSweater', 'collarAndSweater', 'graphicShirt', 'hoodie', 'overall', 'shirtCrewNeck', 'shirtScoopNeck', 'shirtVNeck']
        clothing_colors = ['262e33', '65c9ff', '929598', '3c4f5c', 'ffffff', 'ff5c5c', 'ffafb9', '5199e4', '25557c', 'b1e2ff', 'a7ffc4', 'ffdeb5', 'ffffb1', 'ff488e', 'e6544f']
        eyes_list = ['closed', 'cry', 'default', 'xDizzy', 'eyeRoll', 'happy', 'hearts', 'side', 'squint', 'surprised', 'wink', 'winkWacky']
        eyebrows_list = ['angry', 'angryNatural', 'default', 'defaultNatural', 'flatNatural', 'frownNatural', 'raisedExcited', 'raisedExcitedNatural', 'sadConcerned', 'sadConcernedNatural', 'unibrowNatural', 'upDown', 'upDownNatural']
        mouth_list = ['concerned', 'default', 'disbelief', 'eating', 'grimace', 'sad', 'screamOpen', 'serious', 'smile', 'tongue', 'twinkle', 'vomit']
        
        user.avatar_skin_color = random.choice(skin_colors)
        user.avatar_hair_color = random.choice(hair_colors)
        user.avatar_top = random.choice(tops)
        user.avatar_accessories = random.choice(accessories_list)
        user.avatar_facial_hair = random.choice(facial_hair_list)
        user.avatar_clothing = random.choice(clothing_list)
        user.avatar_clothing_color = random.choice(clothing_colors)
        user.avatar_eyes = random.choice(eyes_list)
        user.avatar_eyebrows = random.choice(eyebrows_list)
        user.avatar_mouth = random.choice(mouth_list)
        user.save()
        
        return Response({
            'message': 'Zufälliger Avatar generiert',
            'avatar': {
                'skinColor': user.avatar_skin_color,
                'hairColor': user.avatar_hair_color,
                'top': user.avatar_top,
                'accessories': user.avatar_accessories,
                'facialHair': user.avatar_facial_hair,
                'clothing': user.avatar_clothing,
                'clothingColor': user.avatar_clothing_color,
                'eyes': user.avatar_eyes,
                'eyebrows': user.avatar_eyebrows,
                'mouth': user.avatar_mouth,
                'url': user.get_avatar_url()
            }
        })