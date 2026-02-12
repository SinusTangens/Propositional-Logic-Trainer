from django.contrib import admin
from .models import SolutionCache

@admin.register(SolutionCache)
class SolutionCacheAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'solver_name', 'created_by', 'created_at']
    search_fields = ['task_id', 'solver_name']