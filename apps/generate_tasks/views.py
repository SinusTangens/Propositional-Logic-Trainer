from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from sympy import srepr

from .models import Task
from .serializers import TaskSerializer
from .services import task_pregeneration_service, TARGET_TASKS_PER_COMBINATION, REFILL_BATCH_SIZE

from core.task_generator.Task import TaskType, DIFFICULTY_CONFIG
from core.task_generator.generate_tasks import TaskGenerator, print_logical_pretty


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Task-Operationen.
    
    Endpunkte:
    - GET    /api/tasks/           - Alle Tasks auflisten
    - POST   /api/tasks/           - Neue Task manuell erstellen
    - GET    /api/tasks/{id}/      - Einzelne Task abrufen
    - DELETE /api/tasks/{id}/      - Task löschen
    - POST   /api/tasks/generate/  - Vorgenerierte Task abrufen (oder on-demand generieren)
    - GET    /api/tasks/pool_status/ - Status des Task-Pools
    """
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Gibt eine vorgenerierte, ungelöste Task zurück.
        
        Verwendet den Pre-Generation-Pool für schnelle Antworten.
        Fallback auf On-Demand-Generierung wenn Pool leer ist.
        
        Request Body:
        {
            "task_type": "DIRECT_INFERENCE" | "CASE_SPLIT",
            "level": 1-4
        }
        """
        task_type_str = request.data.get('task_type', 'DIRECT_INFERENCE')
        level = request.data.get('level', 1)

        # TaskType-Enum ermitteln
        try:
            task_type = TaskType[task_type_str]
        except KeyError:
            return Response(
                {'error': f'Ungültiger task_type: {task_type_str}. Erlaubt: DIRECT_INFERENCE, CASE_SPLIT'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Level validieren
        if (task_type, level) not in DIFFICULTY_CONFIG:
            available_levels = [l for (t, l) in DIFFICULTY_CONFIG.keys() if t == task_type]
            return Response(
                {'error': f'Level {level} für {task_type_str} nicht verfügbar. Verfügbar: {available_levels}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # User-spezifische Task-Auswahl
        user_id = request.user.id if request.user.is_authenticated else None
        
        if user_id:
            # Eingeloggter User: Hole Task die dieser User noch nicht gelöst hat
            db_task = task_pregeneration_service.get_random_unsolved_task_for_user(task_type_str, level, user_id)
        else:
            # Nicht eingeloggt: Hole beliebige Task aus dem Pool
            db_task = Task.objects.filter(task_type=task_type_str, level=level).order_by('?').first()
        
        if db_task:
            # Task gefunden → schnelle Antwort
            serializer = self.get_serializer(db_task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Pool für diesen User ist leer (oder komplett leer)
        # → Batch-Nachgenerierung starten + 1 On-Demand für sofortige Antwort
        if user_id:
            # Asynchron 20 neue Tasks generieren
            task_pregeneration_service.trigger_async_refill(task_type_str, level, count=REFILL_BATCH_SIZE)
        
        # On-Demand: 1 Task sofort generieren für Response
        try:
            db_task = task_pregeneration_service.generate_single_task(task_type, level)
        except Exception as e:
            return Response(
                {'error': f'Task-Generierung fehlgeschlagen: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(db_task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def pool_status(self, request):
        """
        Gibt den Status des Task-Pools zurück.
        
        Response:
        {
            "target_per_combination": 200,
            "refill_batch_size": 20,
            "combinations": [
                {"task_type": "DIRECT_INFERENCE", "level": 1, "total_count": 200, ...},
                ...
            ],
            "total_tasks": 1400,
            "total_target": 1400
        }
        """
        status_list = task_pregeneration_service.get_all_combinations_status()
        total_tasks = sum(s['total_count'] for s in status_list)
        total_target = sum(s['target'] for s in status_list)
        
        return Response({
            'target_per_combination': TARGET_TASKS_PER_COMBINATION,
            'refill_batch_size': REFILL_BATCH_SIZE,
            'combinations': status_list,
            'total_tasks': total_tasks,
            'total_target': total_target
        })

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Filtert Tasks nach Typ und optional Level.
        
        Query-Parameter:
        - task_type: DIRECT_INFERENCE | CASE_SPLIT
        - level: 1-4 (optional)
        """
        task_type = request.query_params.get('task_type')
        level = request.query_params.get('level')

        queryset = self.queryset

        if task_type:
            queryset = queryset.filter(task_type=task_type)
        if level:
            queryset = queryset.filter(level=int(level))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
