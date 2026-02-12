from django.contrib import admin
from .models import FeedbackRule

@admin.register(FeedbackRule)
class FeedbackRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'task_type', 'min_level', 'max_level', 'created_at']
    search_fields = ['name', 'message']