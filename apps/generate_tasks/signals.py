"""
Signals für automatische Task-Nachgenerierung

Wird ausgelöst wenn ein Attempt erstellt wird (= Task wurde "verbraucht").
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import Attempt
from .services import task_pregeneration_service


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Attempt)
def trigger_task_refill_on_attempt(sender, instance: Attempt, created: bool, **kwargs):
    """
    Wird nach jedem neuen Attempt ausgelöst.
    
    Wenn der Attempt neu erstellt wurde, wird geprüft ob Tasks nachgefüllt
    werden müssen und ggf. eine asynchrone Nachgenerierung gestartet.
    """
    if not created:
        return
    
    task = instance.task
    task_type = task.task_type
    level = task.level
    
    # Prüfe ob Nachgenerierung nötig ist
    if task_pregeneration_service.needs_refill(task_type, level):
        logger.info(f"Task-Refill nötig für {task_type} Level {level}")
        task_pregeneration_service.trigger_async_refill(task_type, level)
