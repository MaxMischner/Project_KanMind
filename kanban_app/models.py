"""Models for the KanMind boards application.

This module contains all database models for managing boards, tasks,
comments, and dashboards in the KanMind project management system.
"""

from django.db import models
from django.contrib.auth.models import User


class Dashboard(models.Model):
    """Dashboard model representing a user's personal dashboard.

    Attributes:
        title (str): The title/name of the dashboard (max 255 characters).
        user (User): The owner of the dashboard (foreign key to User model).
    """

    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Board(models.Model):
    """Board model representing a kanban board for project management.

    A board can have multiple members (users) and contains multiple tasks.
    All board members have access to view and edit the board and its tasks.

    Attributes:
        id (int): Auto-incrementing primary key.
        title (str): The title/name of the board (max 255 characters).
        description (str): Detailed description of the board (optional).
        users (ManyToMany): Users who are members of this board.
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, blank=True, null=True)

    def __str__(self):
        """Return string representation of the board.

        Returns:
            str: The title of the board.
        """
        return self.title


class Task(models.Model):
    """Task model representing a work item on a kanban board.

    Each task belongs to a board and can be assigned to a user for completion
    and optionally assigned a reviewer. Tasks track their status through the
    workflow (todo, in progress, done, etc.) and have priority levels.

    Attributes:
        id (int): Auto-incrementing primary key.
        title (str): The title/name of the task (max 255 characters).
        details (str): Detailed description of the task (defaults to empty string).
        board (Board): The board this task belongs to (foreign key).
        due_date (date): Optional deadline for task completion.
        assigned (User): User assigned to complete this task (optional).
        reviewer (User): User assigned to review this task (optional).
        status (str): Current status of the task (default: "todo", max 20 chars).
        priority (str): Priority level of the task (default: "Medium", max 20 chars).
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True, default="")
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    assigned = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviewer',
        null=True,
        blank=True)
    status = models.CharField(max_length=20, default="todo",)
    priority = models.CharField(max_length=20, default='Medium')

    def __str__(self):
        """Return string representation of the task.

        Returns:
            str: The title of the task.
        """
        return self.title


class Comment(models.Model):
    """Comment model representing a comment on a task.

    Users can add comments to tasks to provide updates, ask questions,
    or discuss task details. Comments are timestamped and associated
    with both a task and the board it belongs to.

    Attributes:
        id (int): Auto-incrementing primary key.
        content (str): The text content of the comment.
        task (Task): The task this comment is associated with (foreign key).
        author (User): The user who created this comment (foreign key).
        created_at (datetime): Timestamp when the comment was created (auto-set).
        board (Board): The board this comment belongs to (foreign key).
    """

    id = models.AutoField(primary_key=True)
    content = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
