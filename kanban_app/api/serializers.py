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

    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        """Return author's full name string for frontend display.

        Falls back to email or username if full name is empty.
        """
        name = f"{obj.author.first_name} {obj.author.last_name}".strip()
        if not name:
            name = obj.author.email or obj.author.username
        return name

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['author', 'created_at']


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


class UserNestedSerializer(serializers.ModelSerializer):
    """Minimal user serializer for nested use in responses.
    
    Returns only: id, email, fullname
    Used in nested contexts like board members list or task assignee/reviewer.
    """
    
    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class TaskNestedSerializer(serializers.ModelSerializer):
    """Minimal task serializer for nested use in Board detail responses.
    
    Returns only fields needed by board detail view:
    - id, title, description, status, priority, assignee, reviewer, due_date, comments_count
    
    Excludes board field (redundant in nested context) and comments array.
    """
    
    assignee = UserNestedSerializer(read_only=True, source='assigned')
    reviewer = UserNestedSerializer(read_only=True)
    description = serializers.CharField(source='details', required=False, allow_blank=True)
    comments_count = serializers.SerializerMethodField()
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer for Task list responses (assigned-to-me, reviewing, etc).
    
    Returns fields needed for task list views:
    - id, board, title, description, status, priority, assignee, reviewer, due_date, comments_count
    
    Includes board ID. Excludes comments array and details field.
    """
    
    assignee = UserNestedSerializer(read_only=True, source='assigned')
    reviewer = UserNestedSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='assigned',
        allow_null=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='reviewer',
        allow_null=True)
    description = serializers.CharField(source='details', required=False, allow_blank=True)
    comments_count = serializers.SerializerMethodField()
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def validate_board(self, value):
        """Validate that board exists; raise 404 if not."""
        if value is None:
            raise serializers.ValidationError('Board is required.')
        # Board ID validation already done by PrimaryKeyRelatedField
        return value
    
    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date', 'comments_count']


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Task PATCH/PUT responses.
    
    Returns fields needed for update operations:
    - id, title, description, status, priority, assignee, reviewer, due_date
    
    Excludes board, comments, and comments_count. Uses UserNestedSerializer for assignee/reviewer.
    """
    
    assignee = UserNestedSerializer(read_only=True, source='assigned')
    reviewer = UserNestedSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='assigned',
        allow_null=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='reviewer',
        allow_null=True)
    description = serializers.CharField(source='details', required=False, allow_blank=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model with nested relationships.

    Includes nested serialization for assigned users, reviewers, and comments.
    The 'details' field is handled specially to return empty string instead
    of null for better frontend compatibility. Supports writing assigned and
    reviewer via separate writable fields while reading expanded user objects.
    """

    comments = CommentSerializer(many=True, read_only=True)
    assignee = UserSerializer(read_only=True, source='assigned')
    reviewer = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='assigned')
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='reviewer')
    details = serializers.SerializerMethodField()
    description = serializers.CharField(source='details', required=False, allow_blank=True)

    def get_details(self, obj):
        """Return task details with fallback to empty string.

        Args:
            obj (Task): The Task instance.

        Returns:
            str: Task details or empty string if None.
        """
        return obj.details or ""
    comments_count = serializers.SerializerMethodField()

    def validate_title(self, value):
        """Ensure task title is non-empty after trimming whitespace.

        Args:
            value (str): Proposed task title.

        Returns:
            str: Cleaned title.

        Raises:
            serializers.ValidationError: If title is empty.
        """
        cleaned = (value or "").strip()
        if not cleaned:
            raise serializers.ValidationError('Title cannot be empty.')
        return cleaned

    def validate(self, attrs):
        """Validate status/priority choices, board immutability, and membership.

        - Enforce allowed statuses and priorities.
        - Prevent changing board on update.
        - Ensure assignee/reviewer belong to the task's board (or owner).
        """
        allowed_statuses = {'to-do', 'in-progress', 'review', 'done', 'todo', 'in_progress'}
        allowed_priorities = {'low', 'medium', 'high'}

        raw_status = (attrs.get('status') or '')
        status = raw_status.lower()
        status_normalized = status.replace('_', '-')
        priority = (attrs.get('priority') or '').lower()

        board = attrs.get('board') or getattr(self.instance, 'board', None)
        assignee = attrs.get('assigned')
        reviewer = attrs.get('reviewer')

        if status and status not in allowed_statuses and status_normalized not in allowed_statuses:
            raise serializers.ValidationError({'status': 'Status must be one of to-do, in-progress, review, done.'})
        if priority and priority not in allowed_priorities:
            raise serializers.ValidationError({'priority': 'Priority must be one of low, medium, high.'})

        # Disallow board changes on update
        if self.instance and 'board' in attrs and attrs['board'] != self.instance.board:
            raise serializers.ValidationError({'board': 'Changing board is not allowed.'})

        if board:
            members_qs = board.users.all()
            owner = getattr(board, 'owner', None)
            if assignee and assignee not in members_qs and assignee != owner:
                raise serializers.ValidationError({'assignee_id': 'Assignee must be a board member.'})
            if reviewer and reviewer not in members_qs and reviewer != owner:
                raise serializers.ValidationError({'reviewer_id': 'Reviewer must be a board member.'})

        return attrs

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'details',
            'description',
            'board',
            'due_date',
            'assignee',
            'assignee_id',
            'reviewer',
            'reviewer_id',
            'status',
            'priority',
            'comments',
            'comments_count']

    def get_comments_count(self, obj):
        return obj.comments.count()


class BoardSerializer(serializers.ModelSerializer):
    """Minimal serializer for Board list, POST and PATCH operations.

    Returns only the required fields per API spec:
    - id, title, owner_id, member_count, ticket_count, tasks_to_do_count, tasks_high_prio_count
    
    Used for: GET /api/boards/, POST /api/boards/, PATCH /api/boards/{id}/
    """

    members_write = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='users')
    owner_id = serializers.ReadOnlyField(source='owner.id')
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    def validate_title(self, value):
        """Ensure board title is non-empty after trimming whitespace.

        Args:
            value (str): Proposed board title.

        Returns:
            str: Cleaned title.

        Raises:
            serializers.ValidationError: If title is empty.
        """
        cleaned = (value or "").strip()
        if not cleaned:
            raise serializers.ValidationError('Title cannot be empty.')
        return cleaned

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

    def update(self, instance, validated_data):
        """Update board fields and reset members to provided list.

        Ensures provided members replace existing ones and keeps the owner
        in the members set.
        """
        users_data = validated_data.pop('users', None)
        board = super().update(instance, validated_data)
        if users_data is not None:
            # replace members with provided set and ensure owner is included
            board.users.set(users_data)
            if board.owner:
                board.users.add(board.owner)
        return board

    def get_member_count(self, obj):
        return obj.users.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority__iexact='high').count()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members_write', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count']


class BoardDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single Board GET requests.

    Returns full board data including nested members and tasks arrays
    required by frontend board detail page.
    
    Used for: GET /api/boards/{id}/
    """

    members = UserNestedSerializer(many=True, read_only=True, source='users')
    tasks = TaskNestedSerializer(many=True, read_only=True)
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardPatchSerializer(serializers.ModelSerializer):
    """Serializer for Board PATCH/PUT responses.

    Returns updated board data with owner and members details.
    
    Used for: PATCH /api/boards/{id}/, PUT /api/boards/{id}/
    """

    members_write = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        write_only=True,
        source='users')
    owner_data = UserNestedSerializer(read_only=True, source='owner')
    members_data = UserNestedSerializer(many=True, read_only=True, source='users')

    def validate_title(self, value):
        """Ensure board title is non-empty after trimming whitespace."""
        cleaned = (value or "").strip()
        if not cleaned:
            raise serializers.ValidationError('Title cannot be empty.')
        return cleaned

    def to_internal_value(self, data):
        """Convert frontend field names to model field names."""
        if 'members' in data and 'members_write' not in data:
            data['members_write'] = data.pop('members')
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        """Update board fields and reset members to provided list."""
        users_data = validated_data.pop('users', None)
        board = super().update(instance, validated_data)
        if users_data is not None:
            board.users.set(users_data)
            if board.owner:
                board.users.add(board.owner)
        return board

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data', 'members_write']


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for Dashboard model.

    Handles serialization of user dashboards.
    """

    def validate_title(self, value):
        """Ensure dashboard title is non-empty after trimming whitespace.

        Args:
            value (str): Proposed dashboard title.

        Returns:
            str: Cleaned title.

        Raises:
            serializers.ValidationError: If title is empty.
        """
        cleaned = (value or "").strip()
        if not cleaned:
            raise serializers.ValidationError('Title cannot be empty.')
        return cleaned

    class Meta:
        model = Dashboard
        fields = ['id', 'title', 'user']