from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.generate_tasks.models import Task

# Importiere zentrale Konfiguration aus Task.py
from core.task_generator.Task import (
    TaskType, 
    TASK_TYPE_DISPLAY_NAMES,
    get_max_level,
    get_all_task_types,
    get_total_levels,
)


# ============================================================================
# LEVEL-KONFIGURATION
# Anzahl der benötigten richtigen Antworten in Folge pro Aufgabentyp und Level
# Die Anzahl der Levels wird automatisch aus DIFFICULTY_CONFIG in Task.py abgeleitet!
# Format: { 'TASK_TYPE': { level: required_correct, ... } }
# ============================================================================
LEVEL_CONFIG = {
    'DIRECT_INFERENCE': {
        1: 5,  # Level 1 → 5 richtige zum Aufstieg zu Level 2
        2: 5,  # Level 2 → 5 richtige zum Aufstieg zu Level 3
        3: 3,  # Level 3 → 3 richtige zum Aufstieg zu Level 4
        4: 2,  # Level 4 → 5 richtige zum Abschluss
    },
    'CASE_SPLIT': {
        1: 3,  # Level 1 → 5 richtige zum Aufstieg zu Level 2
        2: 2,  # Level 2 → 5 richtige zum Aufstieg zu Level 3
        3: 1,  # Level 3 → 5 richtige zum Abschluss
    },
}


def get_required_correct(task_type_str: str, level: int) -> int:
    """Holt die benötigte Anzahl richtiger Antworten für ein Level.
    Fallback auf 3 wenn nicht konfiguriert."""
    return LEVEL_CONFIG.get(task_type_str, {}).get(level, 3)


class User(AbstractUser):
    """Custom Nutzer-Modell (erweitert Django's Standard-User)"""
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Statistiken
    total_solved = models.IntegerField(default=0, help_text="Gesamtzahl gelöster Aufgaben")
    correct_solved = models.IntegerField(default=0, help_text="Anzahl korrekt gelöster Aufgaben")
    current_streak = models.IntegerField(default=0, help_text="Aktuelle Streak (seitenübergreifend)")
    highscore_streak = models.IntegerField(default=0, help_text="Höchste Streak aller Zeiten")
    
    # Avatar-Einstellungen für DiceBear (Hex-Farben ohne #)
    avatar_skin_color = models.CharField(max_length=20, default='edb98a', help_text="Hautfarbe (Hex)")
    avatar_hair_color = models.CharField(max_length=20, default='2c1b18', help_text="Haarfarbe (Hex)")
    avatar_top = models.CharField(max_length=50, default='shortFlat', help_text="Frisur/Kopfbedeckung")
    avatar_accessories = models.CharField(max_length=50, default='', blank=True, help_text="Accessoires (Brille etc.)")
    avatar_facial_hair = models.CharField(max_length=50, default='', blank=True, help_text="Bart")
    avatar_clothing = models.CharField(max_length=50, default='blazerAndShirt', help_text="Kleidung")
    avatar_clothing_color = models.CharField(max_length=20, default='e6544f', help_text="Kleidungsfarbe (Hex)")
    avatar_eyes = models.CharField(max_length=30, default='default', help_text="Augen")
    avatar_eyebrows = models.CharField(max_length=30, default='default', help_text="Augenbrauen")
    avatar_mouth = models.CharField(max_length=30, default='default', help_text="Mund")
    
    def get_avatar_url(self):
        """Generiert die DiceBear Avatar-URL basierend auf den Einstellungen.
        
        Verwendet DiceBear 9.x avataaars-neutral Stil mit korrekten Parametern.
        """
        import urllib.parse
        
        # DiceBear 9.x verwendet Arrays für Options-Parameter
        params = {
            'seed': self.username,  # Fallback-Seed für Konsistenz
            'skinColor': [self.avatar_skin_color] if self.avatar_skin_color else [],
            'hairColor': [self.avatar_hair_color] if self.avatar_hair_color else [],
            'top': [self.avatar_top] if self.avatar_top else [],
            'eyes': [self.avatar_eyes] if self.avatar_eyes else [],
            'eyebrows': [self.avatar_eyebrows] if self.avatar_eyebrows else [],
            'mouth': [self.avatar_mouth] if self.avatar_mouth else [],
            'clothing': [self.avatar_clothing] if self.avatar_clothing else [],
            'clothesColor': [self.avatar_clothing_color] if self.avatar_clothing_color else [],
        }
        
        # Optionale Parameter nur wenn gesetzt
        if self.avatar_accessories:
            params['accessories'] = [self.avatar_accessories]
            params['accessoriesProbability'] = 100
        if self.avatar_facial_hair:
            params['facialHair'] = [self.avatar_facial_hair]
            params['facialHairProbability'] = 100
        
        # URL-Parameter erstellen
        query_parts = []
        for key, value in params.items():
            if isinstance(value, list) and value:
                query_parts.append(f'{key}={urllib.parse.quote(value[0])}')
            elif isinstance(value, (int, str)) and value:
                query_parts.append(f'{key}={urllib.parse.quote(str(value))}')
        
        return f"https://api.dicebear.com/9.x/avataaars/svg?{('&'.join(query_parts))}"
    
    class Meta:
        verbose_name = "Nutzer"
        verbose_name_plural = "Nutzer"
    
    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"
    
    def get_progress(self):
        """Holt den aktuellen Fortschritt aus der UserProgress-Tabelle.
        
        Verwendet zentrale Konfiguration aus Task.py für Level-Anzahlen.
        """
        from .models import UserProgress  # Import hier um circular import zu vermeiden
        progress_list = []
        
        # Unit Propagation - verwendet max_level aus DIFFICULTY_CONFIG
        unit_prop = UserProgress.objects.filter(user=self, task_type='DIRECT_INFERENCE').first()
        unit_level = unit_prop.current_level if unit_prop else 1
        unit_max_level = get_max_level(TaskType.DIRECT_INFERENCE)
        progress_list.append({
            'type': TASK_TYPE_DISPLAY_NAMES[TaskType.DIRECT_INFERENCE],
            'task_type': 'DIRECT_INFERENCE',
            'currentLevel': unit_level,
            'totalLevels': unit_max_level,
            'correctInRow': unit_prop.correct_in_row if unit_prop else 0,
            'requiredCorrect': get_required_correct('DIRECT_INFERENCE', unit_level),
            'isUnlocked': True,  # Immer freigeschaltet
            'isCompleted': unit_prop.is_completed if unit_prop else False
        })
        
        # Case Split - nur freigeschaltet wenn Unit Propagation abgeschlossen
        case_split = UserProgress.objects.filter(user=self, task_type='CASE_SPLIT').first()
        case_level = case_split.current_level if case_split else 1
        case_max_level = get_max_level(TaskType.CASE_SPLIT)
        unit_prop_completed = unit_prop.is_completed if unit_prop else False
        progress_list.append({
            'type': TASK_TYPE_DISPLAY_NAMES[TaskType.CASE_SPLIT],
            'task_type': 'CASE_SPLIT',
            'currentLevel': case_level,
            'totalLevels': case_max_level,
            'correctInRow': case_split.correct_in_row if case_split else 0,
            'requiredCorrect': get_required_correct('CASE_SPLIT', case_level),
            'isUnlocked': unit_prop_completed,
            'isCompleted': case_split.is_completed if case_split else False
        })
        
        return progress_list


class UserProgress(models.Model):
    """Speichert den Fortschritt eines Nutzers für jeden Aufgabentyp."""
    
    # TYPE_CHOICES aus zentraler Konfiguration generieren
    TYPE_CHOICES = [
        (tt.name, TASK_TYPE_DISPLAY_NAMES[tt]) 
        for tt in get_all_task_types()
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    current_level = models.IntegerField(default=1)
    correct_in_row = models.IntegerField(default=0, help_text="Anzahl korrekter Antworten in Folge im aktuellen Level")
    is_completed = models.BooleanField(default=False, help_text="Alle Levels abgeschlossen")
    
    class Meta:
        unique_together = ['user', 'task_type']
        verbose_name = "Nutzerfortschritt"
        verbose_name_plural = "Nutzerfortschritte"
    
    def __str__(self):
        return f"{self.user.username} - {self.task_type} Level {self.current_level}"
    
    def record_answer(self, is_correct: bool) -> dict:
        """
        Verarbeitet eine Antwort und aktualisiert den Fortschritt.
        
        Verwendet zentrale Konfiguration aus Task.py für max_level.
        
        Returns:
            dict mit 'level_up', 'type_completed', 'new_level', 'correct_in_row'
        """
        # Max-Level aus zentraler DIFFICULTY_CONFIG holen
        task_type_enum = TaskType[self.task_type]
        max_level = get_max_level(task_type_enum)
        required_correct = get_required_correct(self.task_type, self.current_level)
        
        result = {
            'level_up': False,
            'type_completed': False,
            'new_level': self.current_level,
            'correct_in_row': self.correct_in_row
        }
        
        if is_correct:
            self.correct_in_row += 1
            
            # Prüfen ob genug richtige Antworten für Level-Aufstieg
            if self.correct_in_row >= required_correct:
                if self.current_level < max_level:
                    self.current_level += 1
                    self.correct_in_row = 0
                    result['level_up'] = True
                    result['new_level'] = self.current_level
                else:
                    # Letztes Level abgeschlossen
                    self.is_completed = True
                    result['type_completed'] = True
        else:
            # Bei Fehler: Streak zurücksetzen
            self.correct_in_row = 0
        
        result['correct_in_row'] = self.correct_in_row
        self.save()
        return result


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