from rest_framework import viewsets
from rest_framework.response import Response
from boards_app.api.permissions import IsOwnerOrAdmin
from boards_app.api.serilizers import BoardSerializer, CommentSerializer, TaskSerializer, UserSerializer, DashboardSerializer
from boards_app.models import Board, Comment, Task, Dashboard
from django.contrib.auth.models import User
from rest_framework import generics

class DashboardViewSet(generics.ListAPIView):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsOwnerOrAdmin]

class BoardViewSet(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        # Show only boards where user is a member
        return Board.objects.filter(users=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = BoardSerializer(queryset, many=True)
        return Response(serializer.data)

class BoardDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsOwnerOrAdmin]    

class UserProfilViewSet(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]

class UserProfilDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer    
    permission_classes = [IsOwnerOrAdmin]

class TaskViewSet(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        # Show only tasks from boards where user is a member
        return Task.objects.filter(board__users=self.request.user)

class TaskDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer       
    permission_classes = [IsOwnerOrAdmin]

class CommentViewSet(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer 
    permission_classes = [IsOwnerOrAdmin]

class EmailCheckView(generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin]
    
    def get(self, request):
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
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)
    
    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        serializer.save(task_id=task_id)

class TaskCommentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        return Comment.objects.all()

class AssignedTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        return Task.objects.filter(assigned=self.request.user)

class ReviewerTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)