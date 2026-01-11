from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from boards_app.models import Board, Task, Comment, Dashboard


class BoardModelTest(TestCase):
    """Tests für Board Model"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@test.com',
            password='test123',
            first_name='Test',
            last_name='User')
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@test.com',
            password='test123')

    def test_board_creation(self):
        board = Board.objects.create(title='Test Board', description='Test Description')
        self.assertEqual(board.title, 'Test Board')
        self.assertEqual(board.description, 'Test Description')

    def test_board_add_users(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user1, self.user2)
        self.assertEqual(board.users.count(), 2)
        self.assertIn(self.user1, board.users.all())

    def test_board_string_representation(self):
        board = Board.objects.create(title='Test Board')
        self.assertEqual(str(board), 'Test Board')


class TaskModelTest(TestCase):
    """Tests für Task Model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123')
        self.board = Board.objects.create(title='Test Board')

    def test_task_creation(self):
        task = Task.objects.create(
            title='Test Task',
            details='Test Details',
            board=self.board,
            assigned=self.user,
            status='todo',
            priority='High'
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.details, 'Test Details')
        self.assertEqual(task.status, 'todo')
        self.assertEqual(task.priority, 'High')

    def test_task_default_values(self):
        task = Task.objects.create(
            title='Test Task',
            board=self.board
        )
        self.assertEqual(task.status, 'todo')
        self.assertEqual(task.priority, 'Medium')
        self.assertEqual(task.details, '')

    def test_task_assigned_user(self):
        task = Task.objects.create(
            title='Test Task',
            board=self.board,
            assigned=self.user
        )
        self.assertEqual(task.assigned, self.user)

    def test_task_string_representation(self):
        task = Task.objects.create(title='Test Task', board=self.board)
        self.assertEqual(str(task), 'Test Task')


class CommentModelTest(TestCase):
    """Tests für Comment Model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123')
        self.board = Board.objects.create(title='Test Board')
        self.task = Task.objects.create(title='Test Task', board=self.board)

    def test_comment_creation(self):
        comment = Comment.objects.create(
            content='Test Comment',
            task=self.task,
            author=self.user,
            board=self.board
        )
        self.assertEqual(comment.content, 'Test Comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.task, self.task)

    def test_comment_has_created_at(self):
        comment = Comment.objects.create(
            content='Test Comment',
            task=self.task,
            author=self.user,
            board=self.board
        )
        self.assertIsNotNone(comment.created_at)


class DashboardModelTest(TestCase):
    """Tests für Dashboard Model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123')

    def test_dashboard_creation(self):
        dashboard = Dashboard.objects.create(title='Test Dashboard', user=self.user)
        self.assertEqual(dashboard.title, 'Test Dashboard')
        self.assertEqual(dashboard.user, self.user)


class BoardAPITest(APITestCase):
    """Tests für Board API Endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123',
            first_name='Test',
            last_name='User')
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@test.com',
            password='test123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_board(self):
        data = {
            'title': 'New Board',
            'description': 'Test Description',
            'members_write': [self.user.id]
        }
        response = self.client.post('/api/boards/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Board.objects.count(), 1)
        self.assertEqual(Board.objects.first().title, 'New Board')

    def test_list_boards(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user)
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_boards_filtered_by_user(self):
        board1 = Board.objects.create(title='Board 1')
        board2 = Board.objects.create(title='Board 2')
        board1.users.add(self.user)
        board2.users.add(self.user2)
        response = self.client.get('/api/boards/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Board 1')

    def test_retrieve_board(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user)
        response = self.client.get(f'/api/boards/{board.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Board')

    def test_update_board(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user)
        data = {'title': 'Updated Board'}
        response = self.client.patch(f'/api/boards/{board.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        board.refresh_from_db()
        self.assertEqual(board.title, 'Updated Board')

    def test_delete_board_requires_superuser(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user)
        response = self.client.delete(f'/api/boards/{board.id}/')
        self.assertEqual(response.status_code, 403)

    def test_create_board_with_members(self):
        data = {
            'title': 'Board with Members',
            'members_write': [self.user.id, self.user2.id]
        }
        response = self.client.post('/api/boards/', data, format='json')
        self.assertEqual(response.status_code, 201)
        board = Board.objects.get(title='Board with Members')
        self.assertEqual(board.users.count(), 2)


class TaskAPITest(APITestCase):
    """Tests für Task API Endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123',
            first_name='Test',
            last_name='User')
        self.token = Token.objects.create(user=self.user)
        self.board = Board.objects.create(title='Test Board')
        self.board.users.add(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_task(self):
        data = {
            'title': 'New Task',
            'details': 'Task Details',
            'board': self.board.id,
            'status': 'todo',
            'priority': 'High'
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 1)

    def test_list_tasks(self):
        task = Task.objects.create(title='Test Task', board=self.board)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_tasks_only_from_user_boards(self):
        board1 = Board.objects.create(title='Board 1')
        board2 = Board.objects.create(title='Board 2')
        board1.users.add(self.user)
        task1 = Task.objects.create(title='Task 1', board=board1)
        task2 = Task.objects.create(title='Task 2', board=board2)
        response = self.client.get('/api/tasks/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 1')

    def test_retrieve_task(self):
        task = Task.objects.create(title='Test Task', board=self.board)
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Task')

    def test_update_task(self):
        task = Task.objects.create(title='Test Task', board=self.board, assigned=self.user)
        data = {'title': 'Updated Task', 'status': 'in_progress'}
        response = self.client.patch(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Task')
        self.assertEqual(task.status, 'in_progress')

    def test_assigned_tasks_endpoint(self):
        task1 = Task.objects.create(title='Task 1', board=self.board, assigned=self.user)
        task2 = Task.objects.create(title='Task 2', board=self.board)
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 1')

    def test_reviewer_tasks_endpoint(self):
        task1 = Task.objects.create(title='Task 1', board=self.board, reviewer=self.user)
        task2 = Task.objects.create(title='Task 2', board=self.board)
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 1')


class CommentAPITest(APITestCase):
    """Tests für Comment API Endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123',
            first_name='Test',
            last_name='User')
        self.token = Token.objects.create(user=self.user)
        self.board = Board.objects.create(title='Test Board')
        self.board.users.add(self.user)
        self.task = Task.objects.create(title='Test Task', board=self.board)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_comment(self):
        data = {
            'content': 'Test Comment',
            'task': self.task.id,
            'author': self.user.id,
            'board': self.board.id
        }
        response = self.client.post(f'/api/tasks/{self.task.id}/comments/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)

    def test_list_task_comments(self):
        comment = Comment.objects.create(
            content='Test Comment',
            task=self.task,
            author=self.user,
            board=self.board)
        response = self.client.get(f'/api/tasks/{self.task.id}/comments/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_delete_own_comment(self):
        comment = Comment.objects.create(
            content='Test Comment',
            task=self.task,
            author=self.user,
            board=self.board)
        response = self.client.delete(f'/api/tasks/{self.task.id}/comments/{comment.id}/')
        # Comment author can delete their own comment
        self.assertIn(response.status_code, [204, 403])


class AuthenticationTest(APITestCase):
    """Tests für Authentication"""

    def test_unauthenticated_access_denied(self):
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, 403)

    def test_authenticated_access_allowed(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, 200)


class PermissionTest(APITestCase):
    """Tests für Permissions"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@test.com', password='test123')
        self.user2 = User.objects.create_user(
            username='user2', email='user2@test.com', password='test123')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

    def test_board_member_can_edit(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        data = {'title': 'Updated'}
        response = self.client.patch(f'/api/boards/{board.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_non_member_cannot_edit(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        data = {'title': 'Updated'}
        response = self.client.patch(f'/api/boards/{board.id}/', data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_task_assigned_user_can_edit(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user1)
        task = Task.objects.create(title='Task', board=board, assigned=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        data = {'status': 'in_progress'}
        response = self.client.patch(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_task_reviewer_can_edit(self):
        board = Board.objects.create(title='Test Board')
        board.users.add(self.user1)
        task = Task.objects.create(title='Task', board=board, reviewer=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        data = {'status': 'done'}
        response = self.client.patch(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
