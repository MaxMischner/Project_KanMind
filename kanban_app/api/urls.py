from django.urls import path
from .views import (
    BoardViewSet,
    DashboardViewSet,
    UserProfilViewSet,
    TaskViewSet,
    CommentViewSet,
    EmailCheckView,
    TaskCommentListView,
    TaskCommentDetailView,
    AssignedTasksView,
    ReviewerTasksView,
)

board_list = BoardViewSet.as_view({'get': 'list', 'post': 'create'})
board_detail = BoardViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'})
user_list = UserProfilViewSet.as_view({'get': 'list', 'post': 'create'})
user_detail = UserProfilViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'})
task_list = TaskViewSet.as_view({'get': 'list', 'post': 'create'})
task_detail = TaskViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'})
comment_list = CommentViewSet.as_view({'get': 'list', 'post': 'create'})
comment_detail = CommentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update', 'delete': 'destroy'})

urlpatterns = [
    path(
        'dashboard/',
        DashboardViewSet.as_view(),
        name='dashboard-list'),
    path(
        'boards/',
        board_list,
        name='boards-list'),
    path(
        'boards/<int:pk>/',
        board_detail,
        name='board-detail'),
    path(
        'users/',
        user_list,
        name='userprofil-list'),
    path(
        'users/<int:pk>/',
        user_detail,
        name='userprofil-detail'),
    path(
        'tasks/assigned-to-me/',
        AssignedTasksView.as_view(),
        name='assigned-tasks'),
    path(
        'tasks/reviewing/',
        ReviewerTasksView.as_view(),
        name='reviewer-tasks'),
    path(
        'tasks/',
        task_list,
        name='task-list'),
    path(
        'tasks/<int:pk>/',
        task_detail,
        name='task-detail'),
    path(
        'tasks/<int:task_id>/comments/',
        TaskCommentListView.as_view(),
        name='task-comments'),
    path(
        'tasks/<int:task_id>/comments/<int:pk>/',
        TaskCommentDetailView.as_view(),
        name='task-comment-detail'),
    path(
        'comments/',
        comment_list,
        name='comment-list'),
    path(
        'comments/<int:pk>/',
        comment_detail,
        name='comment-detail'),
    path(
        'email-check/',
        EmailCheckView.as_view(),
        name='email-check'),
]
