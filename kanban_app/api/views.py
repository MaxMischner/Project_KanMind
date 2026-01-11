"""API views for the KanMind boards application.

This module contains all DRF views for managing boards, tasks, comments,
and user profiles. All views require authentication and implement
custom permissions for board member access control.
"""

from rest_framework.response import Response
from kanban_app.api.permissions import IsOwnerOrAdmin
from kanban_app.api.serilizers import BoardSerializer, CommentSerializer, TaskSerializer, UserSerializer, DashboardSerializer
from kanban_app.models import Board, Comment, Task, Dashboard
from django.contrib.auth.models import User
from rest_framework import generics


class DashboardViewSet(generics.ListAPIView):
    """API view for listing user dashboards.

    GET /api/dashboards/ - List all dashboards (filtered by ownership).
    """

    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsOwnerOrAdmin]


class BoardViewSet(generics.ListCreateAPIView):
    """API view for listing and creating boards.

    GET /api/boards/ - List all boards where user is a member.
    POST /api/boards/ - Create a new board.

    Only shows boards where the authenticated user is a member.
    """

    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter boards to only show those where user is a member.

        Returns:
            QuerySet: Boards where the current user is in the members list.
        """
        return Board.objects.filter(users=self.request.user)

    def list(self, request):
        """List all boards for the current user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: JSON array of boards with nested data.
        """
        queryset = self.get_queryset()
        serializer = BoardSerializer(queryset, many=True)
        return Response(serializer.data)


class BoardDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting individual boards.

    GET /api/boards/{id}/ - Retrieve a specific board.
    PATCH /api/boards/{id}/ - Update a board (members only).
    DELETE /api/boards/{id}/ - Delete a board (admin only).
    """

    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrAdmin]


class UserProfilViewSet(generics.ListCreateAPIView):
    """API view for listing and creating user profiles.

    GET /api/users/ - List all users.
    POST /api/users/ - Create a new user.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]


class UserProfilDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting individual user profiles.

    GET /api/users/{id}/ - Retrieve a specific user.
    PATCH /api/users/{id}/ - Update a user profile.
    DELETE /api/users/{id}/ - Delete a user (admin only).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]


class TaskViewSet(generics.ListCreateAPIView):
    """API view for listing and creating tasks.

    GET /api/tasks/ - List all tasks from boards where user is a member.
    POST /api/tasks/ - Create a new task.

    Only shows tasks from boards where the authenticated user is a member.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter tasks to only show those from boards where user is a member.

        Returns:
            QuerySet: Tasks from boards where current user is a member.
        """
        return Task.objects.filter(board__users=self.request.user)


class TaskDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deleting individual tasks.

    GET /api/tasks/{id}/ - Retrieve a specific task.
    PATCH /api/tasks/{id}/ - Update a task (assigned/reviewer/board members).
    DELETE /api/tasks/{id}/ - Delete a task (admin only).
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]


class CommentViewSet(generics.ListCreateAPIView):
    """API view for listing and creating comments.

    GET /api/comments/ - List all comments (filtered by permissions).
    POST /api/comments/ - Create a new comment on a task.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]


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
        serializer.save(task_id=task_id)


class TaskCommentDetailView(generics.RetrieveDestroyAPIView):
    """API view for retrieving and deleting individual comments.

    GET /api/comments/{id}/ - Retrieve a specific comment.
    DELETE /api/comments/{id}/ - Delete a comment (admin only).
    """

    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        """Return all comments.

        Returns:
            QuerySet: All Comment objects.
        """
        return Comment.objects.all()


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
