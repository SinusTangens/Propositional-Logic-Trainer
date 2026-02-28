from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Attempt, UserProgress

User = get_user_model()


class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer für UserProgress-Model."""
    
    type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = ['task_type', 'type_display', 'current_level', 'correct_in_row', 'is_completed']
        read_only_fields = fields


class AvatarSerializer(serializers.ModelSerializer):
    """Serializer für Avatar-Einstellungen."""
    
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'avatar_skin_color', 'avatar_hair_color', 'avatar_top',
            'avatar_accessories', 'avatar_facial_hair', 'avatar_clothing',
            'avatar_clothing_color', 'avatar_eyes', 'avatar_eyebrows', 'avatar_mouth',
            'avatar_url'
        ]
    
    def get_avatar_url(self, obj):
        return obj.get_avatar_url()


class UserSerializer(serializers.ModelSerializer):
    """Serializer für Custom User-Model.
    
    Schließt sensible Felder aus (Passwort, Permissions).
    """
    progress = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'created_at', 'progress', 'stats', 'avatar']
        read_only_fields = ['id', 'created_at']
    
    def get_progress(self, obj):
        """Holt den formatierten Fortschritt für das Frontend."""
        return obj.get_progress()
    
    def get_stats(self, obj):
        """Holt die Statistiken des Nutzers."""
        return {
            'totalSolved': obj.total_solved,
            'correctSolved': obj.correct_solved,
            'currentStreak': obj.current_streak,
            'highscoreStreak': obj.highscore_streak
        }
    
    def get_avatar(self, obj):
        """Holt die Avatar-Einstellungen und URL."""
        return {
            'skinColor': obj.avatar_skin_color,
            'hairColor': obj.avatar_hair_color,
            'top': obj.avatar_top,
            'accessories': obj.avatar_accessories,
            'facialHair': obj.avatar_facial_hair,
            'clothing': obj.avatar_clothing,
            'clothingColor': obj.avatar_clothing_color,
            'eyes': obj.avatar_eyes,
            'eyebrows': obj.avatar_eyebrows,
            'mouth': obj.avatar_mouth,
            'url': obj.get_avatar_url()
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer für die Benutzerregistrierung."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Passwort bestätigen")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Die Passwörter stimmen nicht überein."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        
        # UserProgress für beide Typen erstellen
        UserProgress.objects.create(user=user, task_type='DIRECT_INFERENCE')
        UserProgress.objects.create(user=user, task_type='CASE_SPLIT')
        
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer für Passwortänderung."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Die Passwörter stimmen nicht überein."})
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "Das neue Passwort muss sich vom alten unterscheiden."})
        return attrs


class AttemptSerializer(serializers.ModelSerializer):
    """Serializer für Attempt-Model.
    
    Zeigt User- und Task-Informationen nested an.
    """

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    task_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Attempt
        fields = ['id', 'user', 'user_id', 'task_id', 'solution', 'is_correct', 'feedback', 'timestamp']
        read_only_fields = ['id', 'is_correct', 'feedback', 'timestamp']

    def create(self, validated_data):
        """Überschreibe create(), um user_id und task_id korrekt zu handhaben."""
        from apps.generate_tasks.models import Task

        user_id = validated_data.pop('user_id')
        task_id = validated_data.pop('task_id')

        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id)

        return Attempt.objects.create(user=user, task=task, **validated_data)
