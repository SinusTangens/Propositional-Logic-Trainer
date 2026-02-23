from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from sympy import srepr

from .models import Task
from .serializers import TaskSerializer

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
    - POST   /api/tasks/generate/  - Neue Task automatisch generieren
    """
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generiert eine neue Aufgabe basierend auf task_type und level.
        
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

        # Task generieren
        try:
            generator = TaskGenerator(DIFFICULTY_CONFIG)
            generated_task = generator.generate_task(task_type, level)
        except RuntimeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Prämissen und Variablen in lesbare Strings umwandeln
        premises_str = [print_logical_pretty(p) for p in generated_task.premises]
        premises_sympy = [srepr(p) for p in generated_task.premises]  # SymPy-Repräsentation für fehlerfreies Parsen
        variables_str = [str(v) for v in generated_task.variables]

        # In Datenbank speichern
        db_task = Task.objects.create(
            task_type=task_type_str,
            level=level,
            premises=premises_str,
            premises_sympy=premises_sympy,
            variables=variables_str
        )

        serializer = self.get_serializer(db_task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
