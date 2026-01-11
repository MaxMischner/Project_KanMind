from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class UserRegistrationTest(APITestCase):
    """Tests für Registration Endpoint"""

    def test_registration_successful(self):
        data = {
            'fullname': 'Test User',
            'email': 'testuser@test.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123'
        }
        response = self.client.post('/api/auth/registration/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
        self.assertIn('fullname', response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_registration_password_mismatch(self):
        data = {
            'fullname': 'Test User',
            'email': 'testuser@test.com',
            'password': 'testpass123',
            'repeated_password': 'different123'
        }
        response = self.client.post('/api/auth/registration/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)

    def test_registration_duplicate_email(self):
        User.objects.create_user(
            username='existing',
            email='testuser@test.com',
            password='testpass123')
        data = {
            'fullname': 'Test User',
            'email': 'testuser@test.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123'
        }
        response = self.client.post('/api/auth/registration/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_registration_fullname_split(self):
        data = {
            'fullname': 'John Doe',
            'email': 'john@test.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123'
        }
        response = self.client.post('/api/auth/registration/', data, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='john@test.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

    def test_registration_token_created(self):
        data = {
            'fullname': 'Test User',
            'email': 'testuser@test.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123'
        }
        response = self.client.post('/api/auth/registration/', data, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='testuser@test.com')
        token = Token.objects.get(user=user)
        self.assertIsNotNone(token.key)


class UserLoginTest(APITestCase):
    """Tests für Login Endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_login_successful(self):
        data = {
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
        self.assertIn('fullname', response.data)
        self.assertEqual(response.data['email'], 'test@test.com')
        self.assertEqual(response.data['fullname'], 'Test User')

    def test_login_invalid_email(self):
        data = {
            'email': 'wrong@test.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_password(self):
        data = {
            'email': 'test@test.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_missing_email(self):
        data = {
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_missing_password(self):
        data = {
            'email': 'test@test.com'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, 400)


class EmailCheckTest(APITestCase):
    """Tests für Email Check Endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_email_check_existing_user(self):
        response = self.client.get('/api/email-check/?email=test@test.com')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@test.com')
        self.assertEqual(response.data['fullname'], 'Test User')

    def test_email_check_non_existing_user(self):
        response = self.client.get('/api/email-check/?email=nonexisting@test.com')
        self.assertEqual(response.status_code, 404)

    def test_email_check_missing_parameter(self):
        response = self.client.get('/api/email-check/')
        self.assertEqual(response.status_code, 400)

    def test_email_check_requires_authentication(self):
        self.client.credentials()  # Remove token
        response = self.client.get('/api/email-check/?email=test@test.com')
        self.assertEqual(response.status_code, 403)


class TokenAuthenticationTest(APITestCase):
    """Tests für Token Authentication"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123')
        self.token = Token.objects.create(user=self.user)

    def test_valid_token_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, 200)

    def test_invalid_token_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, 403)

    def test_no_token_authentication(self):
        response = self.client.get('/api/boards/')
        self.assertEqual(response.status_code, 403)

    def test_token_persists_across_requests(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response1 = self.client.get('/api/boards/')
        response2 = self.client.get('/api/boards/')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)


class UserCreationTest(TestCase):
    """Tests für User Model"""

    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_with_special_characters_in_fullname(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Jörg',
            last_name='Müller'
        )
        self.assertEqual(user.first_name, 'Jörg')
        self.assertEqual(user.last_name, 'Müller')
