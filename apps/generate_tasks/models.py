from django.db import models

# Importiere zentrale Konfiguration
from core.task_generator.Task import (
    TASK_TYPE_DISPLAY_NAMES,
    get_all_task_types,
)


class Task(models.Model):

    # TYPE_CHOICES aus zentraler Konfiguration generieren
    TYPE_CHOICES = [
        (tt.name, TASK_TYPE_DISPLAY_NAMES[tt]) 
        for tt in get_all_task_types()
    ]
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    level = models.IntegerField()
    premises = models.JSONField()  # Lesbare Darstellung (Unicode-Symbole)
    premises_sympy = models.JSONField()  # SymPy-Repräsentation (Pflichtfeld, Basis für Lösungserstellung)
    variables = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.task_type} (Level {self.level}) - Prämissen {self.premises}"
    