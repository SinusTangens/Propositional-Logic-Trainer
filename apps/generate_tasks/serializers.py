from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer für Task-Model.
    
    Wandelt Task-Datenbank-Objekte in JSON um und vice versa.
    """

    class Meta:
        model = Task
        fields = ['id', 'task_type', 'level', 'premises', 'variables', 'created_at']
        read_only_fields = ['id', 'created_at']
