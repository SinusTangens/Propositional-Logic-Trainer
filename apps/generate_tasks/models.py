from django.db import models



class Task(models.Model):

    TYPE_CHOICES = [
        ("DIRECT_INFERENCE", "Direct inference"),
        ("CASE_SPLIT", "Case split"),
    ]  # verschiedene Arten von Aufgaben, z.B. direkte Schlussfolgerung, Fallunterscheidung, etc.
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    level = models.IntegerField()
    premises = models.JSONField()  
    variables = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.task_type} (Level {self.level}) - Prämissen {self.premises}"
    