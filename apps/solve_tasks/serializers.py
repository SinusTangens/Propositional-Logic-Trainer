from rest_framework import serializers
from .models import SolutionCache


class SolutionCacheSerializer(serializers.ModelSerializer):
    """Serializer für SolutionCache-Model.
    
    Cache für Solver-Ergebnisse (optional, für Performance).
    """

    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = SolutionCache
        fields = ['id', 'task_id', 'solver_name', 'result', 'created_by_username', 'created_at']
        read_only_fields = ['id', 'created_by_username', 'created_at']
