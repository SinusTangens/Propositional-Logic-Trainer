"""
Tests für die generate_tasks API-Endpunkte.

Deckt ab:
- GET    /api/tasks/           - Alle Tasks auflisten
- POST   /api/tasks/generate/  - Task abrufen/generieren
- GET    /api/tasks/pool_status/ - Status des Task-Pools
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Task
from core.task_generator.Task import TaskType


class TaskModelTest(TestCase):
    """Tests für das Task-Model."""
    
    def test_task_creation(self):
        """Test: Task kann erstellt werden."""
        task = Task.objects.create(
            task_type='DIRECT_INFERENCE',
            level=1,
            premises=['A ⊃ B', 'A'],
            premises_sympy=['Implies(A, B)', 'A'],
            variables=['A', 'B']
        )
        self.assertEqual(task.task_type, 'DIRECT_INFERENCE')
        self.assertEqual(task.level, 1)
        self.assertIsNotNone(task.created_at)
    
    def test_task_str_representation(self):
        """Test: __str__ gibt lesbare Darstellung zurück."""
        task = Task.objects.create(
            task_type='DIRECT_INFERENCE',
            level=1,
            premises=['A ⊃ B', 'A'],
            premises_sympy=['Implies(A, B)', 'A'],
            variables=['A', 'B']
        )
        self.assertIn('DIRECT_INFERENCE', str(task))
        self.assertIn('Level 1', str(task))


class TaskListAPITest(APITestCase):
    """Tests für GET /api/tasks/ - Task-Liste."""
    
    def setUp(self):
        """Erstellt Test-Tasks."""
        self.task1 = Task.objects.create(
            task_type='DIRECT_INFERENCE',
            level=1,
            premises=['A ⊃ B', 'A'],
            premises_sympy=['Implies(A, B)', 'A'],
            variables=['A', 'B']
        )
        self.task2 = Task.objects.create(
            task_type='CASE_SPLIT',
            level=2,
            premises=['A ∨ B', '¬A'],
            premises_sympy=['Or(A, B)', 'Not(A)'],
            variables=['A', 'B']
        )
    
    def test_list_tasks(self):
        """Test: GET /api/tasks/ gibt alle Tasks zurück."""
        url = reverse('task-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_single_task(self):
        """Test: GET /api/tasks/{id}/ gibt einzelne Task zurück."""
        url = reverse('task-detail', kwargs={'pk': self.task1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_type'], 'DIRECT_INFERENCE')
        self.assertEqual(response.data['level'], 1)


class TaskGenerateAPITest(APITestCase):
    """Tests für POST /api/tasks/generate/ - Task generieren."""
    
    def test_generate_direct_inference_task(self):
        """Test: Generiert DIRECT_INFERENCE Task Level 1."""
        url = reverse('task-generate')
        data = {'task_type': 'DIRECT_INFERENCE', 'level': 1}
        
        response = self.client.post(url, data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(response.data['task_type'], 'DIRECT_INFERENCE')
        self.assertEqual(response.data['level'], 1)
        self.assertIn('premises', response.data)
        self.assertIn('variables', response.data)
    
    def test_generate_case_split_task(self):
        """Test: Generiert CASE_SPLIT Task Level 1."""
        url = reverse('task-generate')
        data = {'task_type': 'CASE_SPLIT', 'level': 1}
        
        response = self.client.post(url, data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(response.data['task_type'], 'CASE_SPLIT')
    
    def test_generate_invalid_task_type(self):
        """Test: Ungültiger task_type gibt 400 zurück."""
        url = reverse('task-generate')
        data = {'task_type': 'INVALID_TYPE', 'level': 1}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_generate_invalid_level(self):
        """Test: Ungültiges Level gibt 400 zurück."""
        url = reverse('task-generate')
        data = {'task_type': 'DIRECT_INFERENCE', 'level': 99}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_generate_uses_pool_if_available(self):
        """Test: Generierung nutzt vorgenerierte Tasks aus Pool."""
        # Erstelle vorgenerierte Task
        pregenerated = Task.objects.create(
            task_type='DIRECT_INFERENCE',
            level=1,
            premises=['Vorab', 'Generiert'],
            premises_sympy=['A', 'B'],
            variables=['A', 'B']
        )
        
        url = reverse('task-generate')
        data = {'task_type': 'DIRECT_INFERENCE', 'level': 1}
        
        response = self.client.post(url, data, format='json')
        
        # Sollte 200 zurückgeben (aus Pool) statt 201 (neu generiert)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskPoolStatusAPITest(APITestCase):
    """Tests für GET /api/tasks/pool_status/ - Pool-Status."""
    
    def setUp(self):
        """Erstellt Test-Tasks für Pool."""
        for i in range(5):
            Task.objects.create(
                task_type='DIRECT_INFERENCE',
                level=1,
                premises=[f'P{i}'],
                premises_sympy=[f'P{i}'],
                variables=['A']
            )
    
    def test_pool_status_returns_stats(self):
        """Test: Pool-Status enthält erwartete Felder."""
        url = reverse('task-pool-status')  # DRF action URLs verwenden Bindestrich
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('target_per_combination', response.data)
        self.assertIn('combinations', response.data)
        self.assertIn('total_unsolved', response.data)
    
    def test_pool_status_counts_correctly(self):
        """Test: Pool-Status zählt Tasks korrekt."""
        url = reverse('task-pool-status')  # DRF action URLs verwenden Bindestrich
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Sollte mindestens die 5 erstellten Tasks zählen
        self.assertGreaterEqual(response.data['total_unsolved'], 5)
