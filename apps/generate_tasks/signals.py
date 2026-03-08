"""
Signals für Task-Logging

Hinweis: Die automatische Nachgenerierung wurde entfernt.
Tasks werden nun user-spezifisch verwaltet:
- Jeder User hat seinen eigenen "ungelösten" Pool
- Nachgenerierung erfolgt im View wenn ein User alle Tasks eines Levels gelöst hat
- Batch-Größe: REFILL_BATCH_SIZE (default: 20)
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import Attempt


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Attempt)
def log_attempt_created(sender, instance: Attempt, created: bool, **kwargs):
    """
    Loggt die Erstellung eines neuen Attempts.
    
    Die automatische Nachgenerierung wurde entfernt, da Tasks nun
    user-spezifisch verwaltet werden. Nachgenerierung erfolgt im View
    wenn ein User alle verfügbaren Tasks eines Levels gelöst hat.
    """
    if not created:
        return
    
    task = instance.task
    user = instance.user
    logger.debug(
        f"Attempt erstellt: User {user.username} für Task {task.id} "
        f"({task.task_type} Level {task.level})"
    )
