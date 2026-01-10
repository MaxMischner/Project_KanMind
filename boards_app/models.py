from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Dashboard(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Board(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, blank=True, null=True)
   
    

    def __str__(self):
        return self.title



class Task(models.Model):
    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("doing", "In-progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]
    priority_choices = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    assigned= models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    reviewer= models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewer', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo",)
    priority = models.CharField(max_length=20, choices=priority_choices, default='Medium')
    

    def __str__(self):
        return self.title

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)


    

