"""Custom permission classes for the KanMind boards API.

This module defines custom DRF permission classes that control access
to boards, tasks, and comments based on ownership and admin status.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnlyPermission(BasePermission):
    """Permission class allowing read-only access or staff write access.

    - Anyone can perform safe methods (GET, HEAD, OPTIONS)
    - Only staff users can perform write operations (POST, PUT, PATCH, DELETE)
    """

    def has_permission(self, request, view):
        """Check if user has permission to access the view.

        Args:
            request (Request): The HTTP request.
            view (View): The view being accessed.

        Returns:
            bool: True if request is safe method or user is staff.
        """
        is_staff = bool(request.user and request.user.is_staff)
        return request.method in SAFE_METHODS or is_staff


class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    """Permission class with different rules for different HTTP methods.

    - Safe methods (GET, HEAD, OPTIONS): Anyone can access
    - DELETE: Only superusers (admins) can delete
    - Other methods (POST, PUT, PATCH): Only staff can perform
    """

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the object.

        Args:
            request (Request): The HTTP request.
            view (View): The view being accessed.
            obj: The object being accessed.

        Returns:
            bool: True if user has permission based on HTTP method.
        """
        if request.method in SAFE_METHODS:
            return True
        elif request.method == 'DELETE':
            return bool(request.user and request.user.is_superuser)
        else:
            return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    """Permission class allowing owners or admins to modify objects.

    Implements complex ownership logic for different model types:
    - Board: User must be in the board's users (members) list
    - Task: User must be assigned, reviewer, or board member
    - Comment: User must be the author
    - Dashboard: User must be the owner

    Permission rules:
    - Safe methods (GET, HEAD, OPTIONS): Always allowed for authenticated users
    - DELETE: Only superusers (admins) can delete
    - Other methods (POST, PUT, PATCH): Owner or admin can modify
    """

    def has_permission(self, request, view):
        """Check if user has permission to access the view.

        Args:
            request (Request): The HTTP request.
            view (View): The view being accessed.

        Returns:
            bool: True if user is authenticated.
        """
        return bool(request.user and request.user.is_authenticated)

    def _check_board_ownership(self, request, obj):
        """Check if user is a member of the board.

        Args:
            request (Request): The HTTP request.
            obj (Board): The board object.

        Returns:
            bool: True if user is in the board's members list.
        """
        return request.user == getattr(obj, 'owner', None) or request.user in obj.users.all()

    def _check_task_ownership(self, request, obj):
        """Check if user has access to the task.

        User has access if they are:
        - The assigned user
        - The reviewer
        - The task creator
        - A member of the board the task belongs to

        Args:
            request (Request): The HTTP request.
            obj (Task): The task object.

        Returns:
            bool: True if user has any of the access conditions.
        """
        return (obj.assigned == request.user or
                obj.reviewer == request.user or
                getattr(obj, 'created_by', None) == request.user or
                request.user in obj.board.users.all())

    def _get_ownership_status(self, request, obj):
        """Determine ownership status based on object type.

        Routes to appropriate ownership check based on object attributes:
        - Objects with 'users' attribute -> Board ownership check
        - Objects with 'assigned' and 'reviewer' -> Task ownership check
        - Objects with 'user' attribute -> Direct user ownership
        - Objects with 'author' attribute -> Author ownership

        Args:
            request (Request): The HTTP request.
            obj: The object being checked (Board, Task, Comment, etc.).

        Returns:
            bool: True if user has ownership of the object.
        """
        if hasattr(obj, 'users'):
            return self._check_board_ownership(request, obj)
        elif hasattr(obj, 'assigned') and hasattr(obj, 'reviewer'):
            return self._check_task_ownership(request, obj)
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        return False

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access specific object.

        Permission logic:
        - Safe methods (GET, HEAD, OPTIONS): Always allowed
        - DELETE: Only admins (superusers) can delete
        - Other methods: Owners or admins can modify

        Args:
            request (Request): The HTTP request.
            view (View): The view being accessed.
            obj: The object being accessed.

        Returns:
            bool: True if user has permission for the requested action.
        """
        is_admin = bool(request.user and request.user.is_superuser)
        is_owner = self._get_ownership_status(request, obj)
        is_board = hasattr(obj, 'users')
        is_board_owner = is_board and request.user == getattr(obj, 'owner', None)
        is_task = hasattr(obj, 'board') and hasattr(obj, 'title')

        if request.method in SAFE_METHODS:
            return is_owner or is_admin
        elif request.method == 'DELETE':
            if is_board:
                # Only the board owner or admin may delete
                return is_board_owner or is_admin
            if is_task:
                board_owner = request.user == getattr(obj.board, 'owner', None)
                is_creator = request.user == getattr(obj, 'created_by', None)
                return board_owner or is_creator or is_admin
            return is_owner or is_admin
        else:
            return is_owner or is_admin
