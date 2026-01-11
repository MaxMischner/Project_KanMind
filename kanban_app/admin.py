# Register your models here.
"""Admin configuration for kanban_app models."""

from django.contrib import admin
from kanban_app.models import Board, Task, Comment, Dashboard


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
	"""Admin interface for Board model."""
	list_display = ('id', 'title', 'description')
	search_fields = ('title', 'description')
	filter_horizontal = ('users',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	"""Admin interface for Task model."""
	list_display = ('id', 'title', 'board', 'assigned', 'reviewer', 'status', 'priority', 'due_date')
	list_filter = ('status', 'priority', 'board')
	search_fields = ('title', 'details')
	autocomplete_fields = ('board', 'assigned', 'reviewer')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	"""Admin interface for Comment model."""
	list_display = ('id', 'task', 'author', 'created_at', 'board')
	list_filter = ('created_at', 'board')
	search_fields = ('content',)
	autocomplete_fields = ('task', 'author', 'board')


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
	"""Admin interface for Dashboard model."""
	list_display = ('id', 'title', 'user')
	search_fields = ('title',)
	autocomplete_fields = ('user',)
