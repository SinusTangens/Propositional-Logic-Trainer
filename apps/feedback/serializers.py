from rest_framework import serializers
from .models import FeedbackRule


class FeedbackRuleSerializer(serializers.ModelSerializer):
    """Serializer für FeedbackRule-Model.
    
    Definiert Feedback-Regeln basierend auf Aufgabentyp und Schwierigkeit.
    """

    class Meta:
        model = FeedbackRule
        fields = ['id', 'name', 'task_type', 'min_level', 'max_level', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
