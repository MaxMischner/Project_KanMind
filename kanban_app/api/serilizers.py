"""Serializers for the KanMind boards API.

This module contains DRF serializers that handle conversion between
Python objects and JSON for the boards, tasks, comments, and users.
Includes custom field mapping for frontend compatibility.
"""

from rest_framework import serializers
from kanban_app.models import Board, Dashboard, Task, Comment
from django.contrib.auth.models import User


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model.

    Handles serialization of task comments including author and timestamp.
    """

    class Meta:
        model = Comment
        fields = ['id', 'content', 'task', 'author', 'created_at', 'board']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with fullname field.

    Extends the standard User serializer to include a computed 'fullname'
    field that combines first_name and last_name for frontend display.
    """

    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        """Generate full name from first and last name.

        Args:
            obj (User): The User instance.

        Returns:
            str: Combined first_name and last_name, trimmed of whitespace.
        """
        return f"{obj.first_name} {obj.last_name}".strip()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'fullname']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model with nested relationships.

    Includes nested serialization for assigned users, reviewers, and comments.
    The 'details' field is handled specially to return empty string instead
    of null for better frontend compatibility.
    """

    comments = CommentSerializer(many=True, read_only=True)
    assigned = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        """Return task details with fallback to empty string.

        Args:
            obj (Task): The Task instance.

        Returns:
            str: Task details or empty string if None.
        """
        return obj.details or ""

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'details',
            'board',
            'due_date',
            'assigned',
            'reviewer',
            'status',
            'priority',
            'comments']


class BoardSerializer(serializers.ModelSerializer):
    """Serializer for Board model with custom field mapping.

    Handles frontend-backend field name compatibility by mapping:
    - 'members' (frontend read) <-> 'users' (model field)
    - 'members_write' (frontend write) <-> 'users' (model field)

    Includes nested serialization for board members and tasks.
    """

    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False)
    members = UserSerializer(many=True, read_only=True, source='users')
    members_write = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='users')
    tasks = TaskSerializer(many=True, read_only=True)

    def to_internal_value(self, data):
        """Convert frontend field names to model field names.

        Transforms 'members' to 'members_write' for write operations
        to ensure proper field name mapping during deserialization.

        Args:
            data (dict): The input data from frontend.

        Returns:
            dict: Data with corrected field names for model.
        """
        if 'members' in data and 'members_write' not in data:
            data['members_write'] = data.pop('members')
        return super().to_internal_value(data)

    def create(self, validated_data):
        """Create a new board with members.

        Handles ManyToMany relationship by extracting users data,
        creating the board, then adding users to the relationship.

        Args:
            validated_data (dict): Validated data for board creation.

        Returns:
            Board: The newly created board instance.
        """
        users_data = validated_data.pop('users', [])
        board = Board.objects.create(**validated_data)
        for user in users_data:
            board.users.add(user)
        return board

    def partial_update(self, instance, validated_data):
        """Update board with new members.

        Handles adding new members to the board's ManyToMany relationship.

        Args:
            instance (Board): The board instance being updated.
            validated_data (dict): Validated data containing updates.

        Returns:
            Board: The updated board instance.
        """
        users_data = validated_data.pop('users', None)
        if users_data:
            for user in users_data:
                instance.users.add(user)
        return super().partial_update(instance, validated_data)

    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'users', 'members', 'members_write', 'tasks']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model.

    Duplicate serializer placed here for proper import ordering.
    Handles serialization of task comments.
    """

    class Meta:
        model = Comment
        fields = ['id', 'content', 'task', 'author', 'created_at', 'board']


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for Dashboard model.

    Handles serialization of user dashboards.
    """

    class Meta:
        model = Dashboard
        fields = ['id', 'title', 'user']
