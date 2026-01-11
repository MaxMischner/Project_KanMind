from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsStaffOrReadOnlyPermission(BasePermission):
    """
    Custom permission to only allow read-only access.
    """

    def has_permission(self, request, view):
        is_staff = bool(request.user and request.user.is_staff)
        return request.method in SAFE_METHODS or is_staff
    
class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    """
    Custom permission to only allow admins to delete or patch.
    """

    def has_object_permission(self, request, view, obj):
      if request.method in SAFE_METHODS:
          return True
      elif request.method == 'DELETE':
          return bool(request.user and request.user.is_superuser)
      else:
          return bool(request.user and request.user.is_staff)
      
class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """

    def has_permission(self, request, view):
        # Allow any authenticated user to access the view
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        is_admin = bool(request.user and request.user.is_superuser)
        
        # Check ownership based on model type
        if hasattr(obj, 'users'):  # Board model with ManyToMany
            is_owner = request.user in obj.users.all()
        elif hasattr(obj, 'assigned') and hasattr(obj, 'reviewer'):  # Task model
            # Allow if user is assigned, reviewer, or board member
            is_owner = (obj.assigned == request.user or 
                       obj.reviewer == request.user or 
                       request.user in obj.board.users.all())
        elif hasattr(obj, 'user'):  # Models with ForeignKey to user
            is_owner = obj.user == request.user
        elif hasattr(obj, 'author'):  # Comment model
            is_owner = obj.author == request.user
        else:
            is_owner = False
            
        if request.method in SAFE_METHODS:
            return True
        elif request.method == 'DELETE':
            return is_admin
        else:
            return is_owner or is_admin    