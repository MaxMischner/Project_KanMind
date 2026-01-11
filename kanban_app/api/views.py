"""API views for the KanMind boards application.

This module contains all DRF views for managing boards, tasks, comments,
and user profiles. All views require authentication and implement
custom permissions for board member access control.
"""

from rest_framework import generics, viewsets
from rest_framework.response import Response
from kanban_app.api.permissions import IsOwnerOrAdmin
from kanban_app.api.serializers import BoardSerializer, CommentSerializer, TaskSerializer, UserSerializer, DashboardSerializer
from kanban_app.models import Board, Comment, Task, Dashboard
from django.contrib.auth.models import User


class DashboardViewSet(generics.ListAPIView):
    """API view for listing user dashboards.

    GET /api/dashboards/ - List all dashboards (filtered by ownership).
    """

    serializer_class = DashboardSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Return dashboards owned by the requesting user."""
        return Dashboard.objects.filter(user=self.request.user)


class BoardViewSet(viewsets.ModelViewSet):
    """API view for listing and creating boards.

    GET /api/boards/ - List all boards where user is a member.
    POST /api/boards/ - Create a new board.

    Only shows boards where the authenticated user is a member.
    """

    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Scope list views to member boards; allow full set for object perms.

        For list we filter by membership. For detail actions we return the full
        queryset so object-level permissions can return 403 instead of 404 for
        non-members.
        """
        if getattr(self, 'action', None) == 'list':
            return Board.objects.filter(users=self.request.user)
        return Board.objects.all()

    def perform_create(self, serializer):
        """Create a new board and add creator as member.

        Saves the board and automatically adds the requesting user as a member
        so they can access their own created boards.

        Args:
            serializer (BoardSerializer): The serializer with validated data.
        """
        board = serializer.save()
        board.users.add(self.request.user)


class UserProfilViewSet(viewsets.ModelViewSet):
    """API view for listing and creating user profiles.

    GET /api/users/ - List all users.
    POST /api/users/ - Create a new user.
    """

    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Return all users; can be restricted later if needed."""
        return User.objects.all()


class TaskViewSet(viewsets.ModelViewSet):
    """API view for listing and creating tasks.

    GET /api/tasks/ - List all tasks from boards where user is a member.
    POST /api/tasks/ - Create a new task.

    Only shows tasks from boards where the authenticated user is a member.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter list to member boards; allow full set for object perms."""
        if getattr(self, 'action', None) == 'list':
            return Task.objects.filter(board__users=self.request.user)
        return Task.objects.all()


class CommentViewSet(viewsets.ModelViewSet):
    """API view for listing and creating comments.

    GET /api/comments/ - List all comments (filtered by permissions).
    POST /api/comments/ - Create a new comment on a task.
    """

    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter list to member boards; allow full set for object perms."""
        if getattr(self, 'action', None) == 'list':
            return Comment.objects.filter(task__board__users=self.request.user)
        return Comment.objects.all()


class EmailCheckView(generics.GenericAPIView):
    """API view for checking if an email exists and retrieving user data.

    GET /api/email-check/?email={email} - Check if email exists and get user.

    Used by frontend to look up users by email when adding board members.
    """

    permission_classes = [IsOwnerOrAdmin]

    def get(self, request):
        """Look up a user by email address.

        Args:
            request (Request): HTTP request with 'email' query parameter.

        Returns:
            Response: User data if found, error message otherwise.
        """
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Email parameter is required'}, status=400)

        try:
            user = User.objects.get(email=email)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)


class TaskCommentListView(generics.ListCreateAPIView):
    """API view for listing and creating comments on a specific task.

    GET /api/tasks/{task_id}/comments/ - List all comments for a task.
    POST /api/tasks/{task_id}/comments/ - Add a comment to a task.
    """

    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter comments to only show those for the specified task.

        Returns:
            QuerySet: Comments belonging to the task specified in URL.
        """
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        """Save a new comment with the task_id from URL.

        Args:
            serializer (CommentSerializer): The serializer with validated data.
        """
        task_id = self.kwargs['task_id']
        task = Task.objects.get(pk=task_id)
        serializer.save(task=task, author=self.request.user, board=task.board)


class TaskCommentDetailView(generics.RetrieveDestroyAPIView):
    """API view for retrieving and deleting individual comments.

    GET /api/comments/{id}/ - Retrieve a specific comment.
    DELETE /api/comments/{id}/ - Delete a comment (admin only).
    """

    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Return comments belonging to the target task to enforce scoping."""
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)


class AssignedTasksView(generics.ListAPIView):
    """API view for listing tasks assigned to the current user.

    GET /api/tasks/assigned-to-me/ - List all tasks assigned to current user.

    Returns only tasks where the authenticated user is the assigned person.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter tasks to only show those assigned to current user.

        Returns:
            QuerySet: Tasks where current user is the assigned person.
        """
        return Task.objects.filter(assigned=self.request.user)


class ReviewerTasksView(generics.ListAPIView):
    """API view for listing tasks where current user is the reviewer.

    GET /api/tasks/reviewing/ - List all tasks user is reviewing.

    Returns only tasks where the authenticated user is the reviewer.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter tasks to only show those being reviewed by current user.

        Returns:
            QuerySet: Tasks where current user is the reviewer.
        """
        return Task.objects.filter(reviewer=self.request.user)
