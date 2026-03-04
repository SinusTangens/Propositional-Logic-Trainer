"""
Task Pre-Generation Service

Verantwortlich für:
- Vorgenerierung von Tasks pro task_type/level Kombination
- Nachgenerierung wenn Tasks "verbraucht" werden (= jemand hat einen Attempt dafür)
- Bereitstellung von ungelösten Tasks für Benutzer
"""
import logging
import threading
from typing import Optional, List, Tuple

from django.db.models import Subquery
from sympy import srepr

from .models import Task
from apps.users.models import Attempt
from core.task_generator.Task import TaskType, DIFFICULTY_CONFIG, get_all_task_types, get_levels_for_task_type
from core.task_generator.generate_tasks import TaskGenerator, print_logical_pretty


logger = logging.getLogger(__name__)

# Konfiguration: Anzahl vorgenerierter Tasks pro task_type/level
TARGET_TASKS_PER_COMBINATION = 200

# Maximale Anzahl an Versuchen pro Task bevor übersprungen wird
# Bei Fehlschlag wird die Task übersprungen, aber beim nächsten Attempt
# erneut versucht (Signal-basierte Selbstheilung)
MAX_RETRIES_PER_TASK = 10


class TaskPreGenerationService:
    """Service für Task-Vorgenerierung und -Verwaltung"""
    
    def __init__(self):
        self.generator = TaskGenerator(DIFFICULTY_CONFIG)
        self._lock = threading.Lock()
    
    def get_unsolved_tasks_queryset(self, task_type: str, level: int):
        """
        Gibt QuerySet aller ungelösten Tasks für task_type/level zurück.
        
        Eine Task gilt als "gelöst" sobald IRGENDEIN User einen Attempt dafür hat.
        Das bedeutet: globale Konsumierung der Tasks.
        """
        solved_task_ids = Attempt.objects.values_list('task_id', flat=True)
        return Task.objects.filter(
            task_type=task_type,
            level=level
        ).exclude(id__in=Subquery(solved_task_ids.values('task_id')))
    
    def count_unsolved_tasks(self, task_type: str, level: int) -> int:
        """Zählt ungelöste Tasks für eine Kombination"""
        return self.get_unsolved_tasks_queryset(task_type, level).count()
    
    def get_random_unsolved_task(self, task_type: str, level: int) -> Optional[Task]:
        """
        Holt eine zufällige ungelöste Task für task_type/level.
        Gibt None zurück wenn keine verfügbar ist.
        """
        return self.get_unsolved_tasks_queryset(task_type, level).order_by('?').first()
    
    def needs_refill(self, task_type: str, level: int) -> bool:
        """Prüft ob Tasks nachgefüllt werden müssen"""
        return self.count_unsolved_tasks(task_type, level) < TARGET_TASKS_PER_COMBINATION
    
    def get_refill_count(self, task_type: str, level: int) -> int:
        """Berechnet wie viele Tasks generiert werden müssen"""
        current = self.count_unsolved_tasks(task_type, level)
        return max(0, TARGET_TASKS_PER_COMBINATION - current)
    
    def generate_single_task(self, task_type: TaskType, level: int) -> Task:
        """Generiert eine einzelne Task und speichert sie in der DB"""
        generated = self.generator.generate_task(task_type, level)
        
        premises_str = [print_logical_pretty(p) for p in generated.premises]
        premises_sympy = [srepr(p) for p in generated.premises]
        variables_str = [str(v) for v in generated.variables]
        
        return Task.objects.create(
            task_type=task_type.name,
            level=level,
            premises=premises_str,
            premises_sympy=premises_sympy,
            variables=variables_str
        )
    
    def refill_tasks(self, task_type: str, level: int, count: Optional[int] = None) -> int:
        """
        Füllt Tasks für eine Kombination auf.
        
        Args:
            task_type: String-Name des TaskType (z.B. 'DIRECT_INFERENCE')
            level: Level-Nummer
            count: Optionale Anzahl zu generierender Tasks (sonst bis TARGET)
        
        Returns:
            Anzahl der generierten Tasks
        """
        try:
            tt = TaskType[task_type]
        except KeyError:
            logger.error(f"Ungültiger TaskType: {task_type}")
            return 0
        
        if count is None:
            count = self.get_refill_count(task_type, level)
        
        if count <= 0:
            return 0
        
        generated = 0
        
        for _ in range(count):
            # Versuche mit Retries
            for retry in range(MAX_RETRIES_PER_TASK):
                try:
                    self.generate_single_task(tt, level)
                    generated += 1
                    break
                except RuntimeError:
                    # Retry bei RuntimeError (Task-Generator hat keine passende Task gefunden)
                    if retry < MAX_RETRIES_PER_TASK - 1:
                        continue
                    # Nach allen Retries: Task überspringen, wird beim nächsten Attempt erneut versucht
                    logger.warning(f"Task-Generierung übersprungen nach {MAX_RETRIES_PER_TASK} Versuchen ({task_type}, {level})")
                except Exception as e:
                    logger.error(f"Unerwarteter Fehler bei Task-Generierung ({task_type}, {level}): {e}")
                    break
        
        logger.info(f"Generiert: {generated}/{count} Tasks für {task_type} Level {level}")
        return generated
    
    def refill_all_combinations(self) -> dict:
        """
        Füllt alle task_type/level Kombinationen auf TARGET_TASKS_PER_COMBINATION auf.
        
        Returns:
            Dict mit Statistiken pro Kombination
        """
        stats = {}
        
        for task_type in get_all_task_types():
            for level in get_levels_for_task_type(task_type):
                key = f"{task_type.name}_L{level}"
                before = self.count_unsolved_tasks(task_type.name, level)
                generated = self.refill_tasks(task_type.name, level)
                after = self.count_unsolved_tasks(task_type.name, level)
                
                stats[key] = {
                    'before': before,
                    'generated': generated,
                    'after': after
                }
        
        return stats
    
    def get_all_combinations_status(self) -> List[dict]:
        """Gibt den Status aller Kombinationen zurück"""
        status = []
        
        for task_type in get_all_task_types():
            for level in get_levels_for_task_type(task_type):
                count = self.count_unsolved_tasks(task_type.name, level)
                status.append({
                    'task_type': task_type.name,
                    'level': level,
                    'unsolved_count': count,
                    'target': TARGET_TASKS_PER_COMBINATION,
                    'needs_refill': count < TARGET_TASKS_PER_COMBINATION
                })
        
        return status
    
    def trigger_async_refill(self, task_type: str, level: int):
        """
        Startet Nachgenerierung in einem separaten Thread.
        Für nicht-blockierende Nachgenerierung nach Attempt-Erstellung.
        """
        # Bei Tests deaktivieren (Test-DB unterstützt keine parallelen Zugriffe)
        import sys
        if 'test' in sys.argv:
            logger.debug(f"Async-Refill übersprungen (Test-Modus)")
            return
        
        def refill_worker():
            with self._lock:
                self.refill_tasks(task_type, level)
        
        thread = threading.Thread(target=refill_worker, daemon=True)
        thread.start()
        logger.debug(f"Async-Refill gestartet für {task_type} Level {level}")


# Singleton-Instanz für globalen Zugriff
task_pregeneration_service = TaskPreGenerationService()
