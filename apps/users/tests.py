"""
Tests für die users API-Endpunkte.

Deckt ab:
- POST /api/auth/register/       - Registrierung
- POST /api/auth/login/          - Login
- POST /api/auth/logout/         - Logout
- GET  /api/auth/me/             - Aktueller Nutzer
- POST /api/auth/password-change/ - Passwort ändern
- POST /api/auth/reset-progress/ - Fortschritt zurücksetzen
- POST /api/auth/avatar/         - Avatar aktualisieren
- POST /api/auth/avatar/random/  - Zufälliger Avatar
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import UserProgress, Attempt
from apps.generate_tasks.models import Task


User = get_user_model()


class UserModelTest(TestCase):
    """Tests für das Custom User-Model."""
    
    def test_user_creation(self):
        """Test: User kann mit allen Feldern erstellt werden."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.total_solved, 0)
        self.assertEqual(user.current_streak, 0)
    
    def test_user_get_progress(self):
        """Test: get_progress() gibt strukturierten Fortschritt zurück."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        progress = user.get_progress()
        
        self.assertIsInstance(progress, list)
        self.assertEqual(len(progress), 2)  # DIRECT_INFERENCE und CASE_SPLIT
        
        # Prüfe Struktur
        for p in progress:
            self.assertIn('type', p)
            self.assertIn('task_type', p)
            self.assertIn('currentLevel', p)
            self.assertIn('isUnlocked', p)
    
    def test_user_avatar_url_generation(self):
        """Test: Avatar-URL wird korrekt generiert."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        url = user.get_avatar_url()
        
        self.assertIn('dicebear.com', url)
        self.assertIn('avataaars', url)


class RegisterViewTest(APITestCase):
    """Tests für POST /api/auth/register/ - Registrierung."""
    
    def test_register_success(self):
        """Test: Erfolgreiche Registrierung."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        
        # User sollte in DB existieren
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_password_mismatch(self):
        """Test: Unterschiedliche Passwörter geben Fehler."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'SecurePass123!',
            'password2': 'DifferentPass!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_duplicate_username(self):
        """Test: Doppelter Username gibt Fehler."""
        User.objects.create_user(username='existing', password='pass123!')
        
        url = reverse('register')
        data = {
            'username': 'existing',
            'password': 'NewPass123!',
            'password2': 'NewPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_weak_password(self):
        """Test: Schwaches Passwort wird abgelehnt."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': '123',
            'password2': '123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(APITestCase):
    """Tests für POST /api/auth/login/ - Login."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_success(self):
        """Test: Erfolgreicher Login."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_wrong_password(self):
        """Test: Falsches Passwort gibt 401."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_missing_credentials(self):
        """Test: Fehlende Credentials geben 400."""
        url = reverse('login')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_nonexistent_user(self):
        """Test: Nicht existierender User gibt 401."""
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'somepass'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTest(APITestCase):
    """Tests für POST /api/auth/logout/ - Logout."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_logout_success(self):
        """Test: Erfolgreicher Logout."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_logout_requires_authentication(self):
        """Test: Logout erfordert Login."""
        url = reverse('logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CurrentUserViewTest(APITestCase):
    """Tests für GET /api/auth/me/ - Aktueller Nutzer."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_me_authenticated(self):
        """Test: Authentifizierter Nutzer sieht seine Daten."""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('current-user')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['isAuthenticated'])
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_me_anonymous(self):
        """Test: Anonymer Nutzer bekommt isAuthenticated=False."""
        url = reverse('current-user')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['isAuthenticated'])
        self.assertIsNone(response.data['user'])


class PasswordChangeViewTest(APITestCase):
    """Tests für POST /api/auth/password-change/ - Passwort ändern."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='OldPass123!'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_password_change_success(self):
        """Test: Erfolgreiche Passwortänderung."""
        url = reverse('password-change')
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!',
            'new_password2': 'NewPass456!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Neues Passwort sollte funktionieren
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass456!'))
    
    def test_password_change_wrong_old_password(self):
        """Test: Falsches altes Passwort gibt Fehler."""
        url = reverse('password-change')
        data = {
            'old_password': 'WrongOldPass!',
            'new_password': 'NewPass456!',
            'new_password2': 'NewPass456!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_change_requires_authentication(self):
        """Test: Passwortänderung erfordert Login."""
        self.client.force_authenticate(user=None)
        
        url = reverse('password-change')
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass456!',
            'new_password2': 'NewPass456!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ResetProgressViewTest(APITestCase):
    """Tests für POST /api/auth/reset-progress/ - Fortschritt zurücksetzen."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.total_solved = 50
        self.user.correct_solved = 40
        self.user.current_streak = 5
        self.user.highscore_streak = 10
        self.user.save()
        
        # Erstelle Progress
        UserProgress.objects.create(
            user=self.user,
            task_type='DIRECT_INFERENCE',
            current_level=3,
            correct_in_row=2
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_reset_progress_success(self):
        """Test: Fortschritt wird zurückgesetzt."""
        url = reverse('reset-progress')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_solved, 0)
        self.assertEqual(self.user.correct_solved, 0)
        self.assertEqual(self.user.current_streak, 0)
        self.assertEqual(self.user.highscore_streak, 0)
    
    def test_reset_progress_resets_user_progress(self):
        """Test: UserProgress-Einträge werden zurückgesetzt."""
        url = reverse('reset-progress')
        self.client.post(url)
        
        progress = UserProgress.objects.get(user=self.user, task_type='DIRECT_INFERENCE')
        self.assertEqual(progress.current_level, 1)
        self.assertEqual(progress.correct_in_row, 0)
    
    def test_reset_progress_requires_authentication(self):
        """Test: Reset erfordert Login."""
        self.client.force_authenticate(user=None)
        
        url = reverse('reset-progress')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UpdateAvatarViewTest(APITestCase):
    """Tests für POST /api/auth/avatar/ - Avatar aktualisieren."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_update_avatar_success(self):
        """Test: Avatar-Felder werden aktualisiert."""
        url = reverse('update-avatar')
        data = {
            'skinColor': 'ffdbb4',
            'hairColor': 'b58143',
            'eyes': 'happy'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avatar', response.data)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar_skin_color, 'ffdbb4')
        self.assertEqual(self.user.avatar_hair_color, 'b58143')
        self.assertEqual(self.user.avatar_eyes, 'happy')
    
    def test_update_avatar_returns_url(self):
        """Test: Response enthält Avatar-URL."""
        url = reverse('update-avatar')
        data = {'eyes': 'wink'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertIn('url', response.data['avatar'])
        self.assertIn('dicebear.com', response.data['avatar']['url'])
    
    def test_update_avatar_requires_authentication(self):
        """Test: Avatar-Update erfordert Login."""
        self.client.force_authenticate(user=None)
        
        url = reverse('update-avatar')
        data = {'eyes': 'happy'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RandomizeAvatarViewTest(APITestCase):
    """Tests für POST /api/auth/avatar/random/ - Zufälliger Avatar."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_randomize_avatar_success(self):
        """Test: Avatar wird randomisiert."""
        # Speichere originale Werte
        original_skin = self.user.avatar_skin_color
        original_hair = self.user.avatar_hair_color
        
        url = reverse('randomize-avatar')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avatar', response.data)
        
        # Mindestens ein Wert sollte sich ändern (bei mehrfachen Versuchen)
        # Da es zufällig ist, prüfen wir nur ob Response-Struktur stimmt
        self.assertIn('skinColor', response.data['avatar'])
        self.assertIn('url', response.data['avatar'])
    
    def test_randomize_avatar_requires_authentication(self):
        """Test: Randomize erfordert Login."""
        self.client.force_authenticate(user=None)
        
        url = reverse('randomize-avatar')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserProgressModelTest(TestCase):
    """Tests für das UserProgress-Model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_progress_creation(self):
        """Test: UserProgress kann erstellt werden."""
        progress = UserProgress.objects.create(
            user=self.user,
            task_type='DIRECT_INFERENCE',
            current_level=1,
            correct_in_row=0
        )
        
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.task_type, 'DIRECT_INFERENCE')
    
    def test_progress_record_correct_answer(self):
        """Test: record_answer() erhöht correct_in_row bei korrekter Antwort."""
        progress = UserProgress.objects.create(
            user=self.user,
            task_type='DIRECT_INFERENCE',
            current_level=1,
            correct_in_row=0
        )
        
        progress.record_answer(is_correct=True)
        
        self.assertEqual(progress.correct_in_row, 1)
    
    def test_progress_record_wrong_answer_resets(self):
        """Test: record_answer() setzt correct_in_row bei falscher Antwort zurück."""
        progress = UserProgress.objects.create(
            user=self.user,
            task_type='DIRECT_INFERENCE',
            current_level=1,
            correct_in_row=3
        )
        
        progress.record_answer(is_correct=False)
        
        self.assertEqual(progress.correct_in_row, 0)
