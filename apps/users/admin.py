from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Attempt

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ['username', 'email', 'is_staff', 'created_at']
    search_fields = ['username', 'email']

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'is_correct', 'timestamp']
    list_filter = ['is_correct', 'timestamp']
    search_fields = ['user__username', 'task__id']