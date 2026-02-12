from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.generate_tasks.models import Task



class User(AbstractUser):
    """Custom Nutzer-Modell (erweitert Django's Standard-User)"""
    
    # Optional: Extra-Felder für deinen Use-Case
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Nutzer"
        verbose_name_plural = "Nutzer"
    
    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Attempt(models.Model):
    """Modell für einen Lösungsversuch eines Nutzers"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="Welcher Nutzer hat diesen Versuch gemacht?"
    )
    
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE,
        help_text="Welche Aufgabe wurde gelöst?"
    )
    
    solution = models.JSONField(
        help_text="Die Lösung des Nutzers als JSON"
    )
    
    is_correct = models.BooleanField(
        default=False,
        help_text="Ist die Lösung korrekt?"
    )
    
    feedback = models.TextField(
        blank=True,
        help_text="Rückmeldung für den Nutzer"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'task']),
        ]
        verbose_name = "Lösungsversuch"
        verbose_name_plural = "Lösungsversuche"
    
    def __str__(self):
        return f"Attempt: {self.user.username} - Task {self.task.id} - {'Richtig' if self.is_correct else 'Falsch'}"