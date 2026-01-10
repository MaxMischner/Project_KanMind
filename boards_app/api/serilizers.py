from rest_framework import serializers
from boards_app.models import Board, Dashboard, Task, Comment
from django.contrib.auth.models import User

class CommentSerializer(serializers.ModelSerializer): 

    class Meta:
        model = Comment
        fields = ['id', 'content', 'task', 'author', 'created_at', 'board']

class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'fullname']

class TaskSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    assigned = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'details', 'board', 'due_date', 'assigned', 'reviewer', 'status', 'priority', 'comments']




class BoardSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    members = UserSerializer(many=True, read_only=True, source='users')
    members_write = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False, write_only=True, source='users')
    tasks = TaskSerializer(many=True, read_only=True)

    def to_internal_value(self, data):
        # Wenn "members" im Request ist, konvertiere zu "members_write"
        if 'members' in data and 'members_write' not in data:
            data['members_write'] = data.pop('members')
        return super().to_internal_value(data)

    def partial_update(self, instance, validated_data):
        users_data = validated_data.pop('users', None)
        if users_data:
            for user_data in users_data:
                user, created = User.objects.get_or_create(**user_data)
                instance.users.add(user)
        return super().partial_update(instance, validated_data)
    

    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'users', 'members', 'members_write', 'tasks']



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'task', 'author', 'created_at', 'board']



class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = ['id', 'title', 'user']