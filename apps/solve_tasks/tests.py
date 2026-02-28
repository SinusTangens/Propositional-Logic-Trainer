"""
Tests für die solve_tasks API-Endpunkte.

Deckt ab:
- POST /api/solve/              - Aufgabe lösen
- POST /api/feedback/           - Feedback abrufen
- GET  /api/solution/{task_id}/ - Lösung abrufen

Alle Endpunkte erfordern Authentifizierung.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.generate_tasks.models import Task
from .models import SolutionCache


User = get_user_model()


class SolveTaskBaseTest(APITestCase):
    """Basis-Klasse mit gemeinsamen Setup-Methoden."""
    
    def setUp(self):
        """Erstellt Test-User und Task."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Einfache Task bei der A=True abgeleitet werden kann
        # A → B, A ⊢ A=True, B=True
        self.task = Task.objects.create(
            task_type='DIRECT_INFERENCE',
            level=1,
            premises=['A ⊃ B', 'A'],
            premises_sympy=['Implies(A, B)', 'A'],
            variables=['A', 'B']
        )
        
        self.client.force_authenticate(user=self.user)


class SolveTaskAPITest(SolveTaskBaseTest):
    """Tests für POST /api/solve/ - Aufgabe lösen."""
    
    def test_solve_requires_authentication(self):
        """Test: /api/solve/ erfordert Login."""
        self.client.force_authenticate(user=None)
        
        url = reverse('solve-task')
        data = {'task_id': self.task.id, 'answers': {'A': 'True', 'B': 'True'}}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_solve_missing_task_id(self):
        """Test: Fehlende task_id gibt 400 zurück."""
        url = reverse('solve-task')
        data = {'answers': {'A': 'True'}}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_solve_task_not_found(self):
        """Test: Nicht existierende Task gibt 404 zurück."""
        url = reverse('solve-task')
        data = {'task_id': 99999, 'answers': {'A': 'True'}}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_solve_correct_answer(self):
        """Test: Korrekte Antwort wird erkannt."""
        url = reverse('solve-task')
        # A → B, A ⊢ A=True, B=True
        data = {
            'task_id': self.task.id,
            'answers': {'A': 'True', 'B': 'True'}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_correct', response.data)
        self.assertIn('results', response.data)
        self.assertIn('progress', response.data)
        self.assertIn('stats', response.data)
    
    def test_solve_wrong_answer(self):
        """Test: Falsche Antwort wird erkannt."""
        url = reverse('solve-task')
        data = {
            'task_id': self.task.id,
            'answers': {'A': 'False', 'B': 'False'}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_correct'])
    
    def test_solve_updates_user_stats(self):
        """Test: Lösen aktualisiert Nutzer-Statistiken."""
        initial_total = self.user.total_solved
        
        url = reverse('solve-task')
        data = {
            'task_id': self.task.id,
            'answers': {'A': 'True', 'B': 'True'}
        }
        
        self.client.post(url, data, format='json')
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_solved, initial_total + 1)
    
    def test_solve_returns_per_variable_results(self):
        """Test: Antwort enthält Ergebnisse pro Variable."""
        url = reverse('solve-task')
        data = {
            'task_id': self.task.id,
            'answers': {'A': 'True', 'B': 'False'}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertIn('A', response.data['results'])
        self.assertIn('B', response.data['results'])
        self.assertIn('user_answer', response.data['results']['A'])
        self.assertIn('correct_answer', response.data['results']['A'])
        self.assertIn('is_correct', response.data['results']['A'])


class GetFeedbackAPITest(SolveTaskBaseTest):
    """Tests für POST /api/feedback/ - Feedback abrufen."""
    
    def test_feedback_requires_authentication(self):
        """Test: /api/feedback/ erfordert Login."""
        self.client.force_authenticate(user=None)
        
        url = reverse('get-feedback')
        data = {
            'task_id': self.task.id,
            'variable': 'A',
            'user_answer': 'True'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_feedback_missing_parameters(self):
        """Test: Fehlende Parameter geben 400 zurück."""
        url = reverse('get-feedback')
        data = {'task_id': self.task.id}  # variable und user_answer fehlen
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_feedback_task_not_found(self):
        """Test: Nicht existierende Task gibt 404 zurück."""
        url = reverse('get-feedback')
        data = {
            'task_id': 99999,
            'variable': 'A',
            'user_answer': 'True'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_feedback_returns_feedback_text(self):
        """Test: Feedback-Endpunkt gibt Feedback-Text zurück."""
        url = reverse('get-feedback')
        data = {
            'task_id': self.task.id,
            'variable': 'A',
            'user_answer': 'False'  # Falsche Antwort für Feedback
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('variable', response.data)
        self.assertIn('feedback', response.data)
        self.assertEqual(response.data['variable'], 'A')


class GetSolutionAPITest(SolveTaskBaseTest):
    """Tests für GET /api/solution/{task_id}/ - Lösung abrufen."""
    
    def test_solution_requires_authentication(self):
        """Test: /api/solution/ erfordert Login."""
        self.client.force_authenticate(user=None)
        
        url = reverse('get-solution', kwargs={'task_id': self.task.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_solution_task_not_found(self):
        """Test: Nicht existierende Task gibt 404 zurück."""
        url = reverse('get-solution', kwargs={'task_id': 99999})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_solution_returns_solution(self):
        """Test: Lösung wird korrekt zurückgegeben."""
        url = reverse('get-solution', kwargs={'task_id': self.task.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('solution', response.data)
        self.assertIn('cached', response.data)
        # Lösung sollte alle Variablen enthalten
        self.assertIn('A', response.data['solution'])
        self.assertIn('B', response.data['solution'])
    
    def test_solution_caches_result(self):
        """Test: Lösung wird gecacht."""
        url = reverse('get-solution', kwargs={'task_id': self.task.id})
        
        # Erster Aufruf - sollte berechnen
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Prüfe ob Cache erstellt wurde
        cache_exists = SolutionCache.objects.filter(task_id=self.task.id).exists()
        self.assertTrue(cache_exists)
        
        # Zweiter Aufruf - sollte aus Cache kommen
        response2 = self.client.get(url)
        self.assertTrue(response2.data['cached'])


class SolutionCacheModelTest(TestCase):
    """Tests für das SolutionCache-Model."""
    
    def setUp(self):
        self.task = Task.objects.create(
            task_type='DIRECT_INFERENCE',
            level=1,
            premises=['A'],
            premises_sympy=['A'],
            variables=['A']
        )
    
    def test_cache_creation(self):
        """Test: Cache-Eintrag kann erstellt werden."""
        cache = SolutionCache.objects.create(
            task_id=self.task.id,  # Model verwendet task_id (IntegerField)
            solver_name='bucket_elimination',
            result={'A': 'True'}
        )
        
        self.assertEqual(cache.task_id, self.task.id)
        self.assertEqual(cache.result['A'], 'True')
    
    def test_cache_unique_per_task_and_solver(self):
        """Test: Cache kann pro Task+Solver aktualisiert werden."""
        SolutionCache.objects.create(
            task_id=self.task.id,
            solver_name='bucket_elimination',
            result={'A': 'True'}
        )
        
        # Update anstatt zweiter Eintrag sollte funktionieren
        SolutionCache.objects.update_or_create(
            task_id=self.task.id,
            solver_name='bucket_elimination',
            defaults={'result': {'A': 'False'}}
        )
        
        # Sollte nur einen Eintrag geben
        count = SolutionCache.objects.filter(task_id=self.task.id).count()
        self.assertEqual(count, 1)
