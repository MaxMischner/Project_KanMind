# KanMind - Kanban Board Project Management System

![KanMind Logo](assets/icons/logo_icon.svg)

**KanMind** is a project management application with a Django REST Framework backend. This repository contains the backend only; the frontend is maintained in a separate repository. It provides a kanban-style board system for managing tasks, assigning team members, and tracking project progress.

---

## ⚠️ Important: Authentication Token Reset

**If you experience 403 Forbidden errors or authentication issues after database reset:**

The frontend stores authentication tokens in localStorage. After resetting the database, old tokens become invalid. To resolve this:

1. Open your browser's Developer Console (F12)
2. Navigate to the **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Select **Local Storage** → `http://127.0.0.1:5500`
4. Click **Clear All** or delete the following keys:
   - `auth-token`
   - `auth-user-id`
   - `auth-email`
   - `auth-fullname`
5. Reload the page and log in again with valid credentials

**Quick Console Command:**
```javascript
localStorage.clear();
```

> **Note:** This manual step is required because the frontend authentication guard was not modified to automatically redirect on 401/403 responses.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Special Features](#special-features)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [License](#license)

---

## Features

### Core Functionality
- **User Authentication**: Email-based registration and login with token authentication
- **Board Management**: Create, edit, and delete kanban boards with multiple members
- **Task Management**: Full CRUD operations for tasks with status tracking (todo, in progress, done)
- **Task Assignment**: Assign tasks to users and designate reviewers
- **Task Filtering**: View tasks assigned to you or tasks you're reviewing
- **Comments**: Add comments to tasks for collaboration
- **Priority Levels**: Set task priorities (Low, Medium, High)
- **Due Dates**: Assign deadlines to tasks
- **Real-time Updates**: Frontend automatically reflects backend changes

### Security & Permissions
- Token-based authentication (DRF Token Authentication)
- Custom permission classes for board member access control
- Only board members can view and edit tasks
- Only admins can delete boards and tasks
- Author-only comment deletion

---

## Technology Stack

### Backend
- **Python 3.x**
- **Django 6.0.1** - Web framework
- **Django REST Framework 3.15.2** - API framework
- **SQLite3** - Database (can be changed to PostgreSQL/MySQL)
- **django-cors-headers** - CORS support for frontend-backend communication

### Frontend (separate repository)
- Vanilla JavaScript (ES6+), HTML5 & CSS3
- Served via VS Code Live Server
- Not included in this backend repository

### Development Tools
- **coverage.py** - Test coverage reporting (97% coverage achieved)
- **flake8** - PEP8 compliance checking
- **autopep8** - Automatic code formatting

---

## Prerequisites

Before running this project, ensure you have the following installed:

- **Python 3.8+** ([Download here](https://www.python.org/downloads/))
- **pip** (Python package manager, usually comes with Python)
- **Visual Studio Code** ([Download here](https://code.visualstudio.com/))
- **VS Code Live Server Extension** ([Install from VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer))

---

## Installation & Setup

### 1. Clone or Download the Project

```bash
cd C:\Users\YourUsername\Desktop\Backend\Python\Project_KanMind
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

**Required packages** (from `requirements.txt`):
```
Django==6.0.1
djangorestframework==3.15.2
django-cors-headers==4.6.0
coverage==7.6.10
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

This creates the SQLite database and all necessary tables.

### 5. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account. You can use this to access the Django admin panel at `http://127.0.0.1:8000/admin/`.

---

## Running the Project

### Start the Backend Server

```bash
python manage.py runserver
```

The backend API will be available at: **http://127.0.0.1:8000/**

### Frontend (optional)

The frontend runs from a separate repository. If you use it locally, start it via VS Code Live Server (default port 5500) and ensure the backend is running at port 8000. CORS is configured for `http://127.0.0.1:5500`.

---

## Project Structure

```
Project_KanMind/
├── core/                         # Django project (settings, urls, wsgi, asgi)
│   ├── settings.py               # Project configuration
│   ├── urls.py                   # Main URL routing
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
│
├── kanban_app/                   # Kanban functionality (boards, tasks, comments)
│   ├── models.py                 # Database models: Board, Task, Comment, Dashboard
│   ├── admin.py                  # Admin registrations and configuration
│   ├── tests.py                  # Comprehensive tests
│   └── api/
│       ├── serializers.py        # DRF serializers with field mapping
│       ├── views.py              # API views and endpoints
│       ├── permissions.py        # Custom permission classes
│       └── urls.py               # Kanban API URL routing
│
├── auth_app/                     # Authentication (registration, login, profiles)
│   ├── admin.py                  # Admin (User is handled by Django)
│   ├── tests.py                  # Authentication tests
│   └── api/
│       ├── serializers.py        # Registration & login serializers
│       ├── views.py              # Auth endpoints
│       └── urls.py               # Auth API URL routing
│
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/registration/` | Register a new user (returns token) |
| POST | `/api/auth/login/` | Login with email & password (returns token) |
| GET | `/api/email-check/?email={email}` | Check if email exists and get user data |

**Registration Request Example:**
```json
{
  "fullname": "Max Mueller",
  "email": "max@example.com",
  "password": "securepass123",
  "repeated_password": "securepass123"
}
```

**Login Request Example:**
```json
{
  "email": "max@example.com",
  "password": "securepass123"
}
```

### Board Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/boards/` | List all boards (user is member of) |
| POST | `/api/boards/` | Create a new board |
| GET | `/api/boards/{id}/` | Retrieve a specific board |
| PATCH | `/api/boards/{id}/` | Update a board (members only) |
| DELETE | `/api/boards/{id}/` | Delete a board (admin only) |

### Task Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/` | List all tasks (from user's boards) |
| POST | `/api/tasks/` | Create a new task |
| GET | `/api/tasks/{id}/` | Retrieve a specific task |
| PATCH | `/api/tasks/{id}/` | Update a task |
| DELETE | `/api/tasks/{id}/` | Delete a task (admin only) |
| GET | `/api/tasks/assigned-to-me/` | List tasks assigned to current user |
| GET | `/api/tasks/reviewing/` | List tasks user is reviewing |

### Comment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/{task_id}/comments/` | List all comments for a task |
| POST | `/api/tasks/{task_id}/comments/` | Add a comment to a task |
| DELETE | `/api/comments/{id}/` | Delete a comment (admin only) |

### Authentication Headers

All API requests (except registration and login) require an authentication token:

```
Authorization: Token YOUR_TOKEN_HERE
```

---

## Special Features

### 1. Email-Based Authentication
Unlike standard Django authentication that uses usernames, KanMind uses **email addresses** as the primary login identifier. The email is stored as both the username and email field for consistency.

### 2. Fullname Field Handling
During registration, users provide a single "fullname" field. The backend automatically:
- Splits the fullname into `first_name` and `last_name`
- Stores them separately in the database
- Combines them back to "fullname" in API responses

### 3. Frontend-Backend Field Mapping
The serializers implement custom field name mapping:
- **Frontend uses**: `members` (for board users)
- **Backend model uses**: `users` (ManyToManyField)
- **Serializer handles**: Automatic conversion via `to_internal_value()` method

### 4. Task Details Default Value
Task details field returns empty string `""` instead of `null` to prevent frontend "undefined" errors.

### 5. Nested Serialization
API responses include nested objects:
- Board responses include full user objects for members
- Task responses include full user objects for assigned/reviewer
- Task responses include all related comments

### 6. Board Member Filtering
Users only see:
- Boards they are members of
- Tasks from boards they are members of
- This ensures data privacy and security

### 7. Permission System
Custom `IsOwnerOrAdmin` permission class that:
- Allows board members to edit boards and tasks
- Allows task assigned users and reviewers to edit tasks
- Restricts deletion to admins only
- Checks ownership dynamically based on model type

### 8. CORS Configuration
CORS is configured to allow requests from:
- `http://127.0.0.1:5500` (Live Server default port)
- `http://localhost:5500` (alternative)

To add more origins, edit `CORS_ALLOWED_ORIGINS` in `settings.py`.

### 9. CSRF Disabled for API
`CsrfViewMiddleware` is removed from middleware to allow API requests without CSRF tokens (token authentication is used instead).

---

## Testing

### Run All Tests

```bash
python manage.py test
```

**Output:**
```
Ran 53 tests in 32.323s
OK
```

### Test Coverage

Generate coverage report:

```bash
# Run tests with coverage
coverage run --source='.' manage.py test

# Generate terminal report
coverage report

# Generate HTML report
coverage html
```

Open `htmlcov/index.html` in your browser to see detailed coverage.

**Current Coverage: 97%** ✅

### Test Structure

- **boards_app/tests.py**: 35+ tests covering:
  - Board CRUD operations
  - Task CRUD operations
  - Comment functionality
  - Permission checks
  - Filtering (assigned/reviewer tasks)

- **user_auth_app/tests.py**: 18+ tests covering:
  - User registration
  - Email-based login
  - Password validation
  - Email uniqueness
  - Token authentication

---

## Code Quality

This project follows strict code quality standards:

### PEP8 Compliance ✅
All Python code follows PEP8 style guidelines.

**Check compliance:**
```bash
flake8 .
```

**Auto-fix issues:**
```bash
autopep8 --in-place --aggressive --aggressive -r .
```

### Code Quality Standards Met:
- ✅ **Test Coverage**: 97% (requirement: 95%)
- ✅ **PEP8 Compliant**: All code formatted correctly
- ✅ **Function Size**: All functions ≤14 lines
- ✅ **Single Responsibility**: Each function has one clear purpose
- ✅ **Documentation**: All classes and methods documented in English
- ✅ **No Commented Code**: No commented-out code in repository
- ✅ **No Print Statements**: All debug prints removed

---

## Configuration

### Change Database (Optional)

To use PostgreSQL or MySQL instead of SQLite, edit `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kanmind_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Change Frontend Port

If Live Server uses a different port, update `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:YOUR_PORT',
    'http://localhost:YOUR_PORT',
]
```

### Change API Base URL

If backend runs on a different port, update `shared/js/config.js`:

```javascript
const BASE_URL = 'http://127.0.0.1:YOUR_PORT/api/';
```

---

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Ensure migrations are applied: `python manage.py migrate`
- Verify virtual environment is activated

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL

### Authentication errors
- Clear browser localStorage: `localStorage.clear()`
- Check if token is being sent in Authorization header
- Verify user exists in database

### Tests failing
- Run migrations: `python manage.py migrate`
- Check if test database exists
- Use `--keepdb` flag to preserve test database between runs

---

## Development

### Adding New Features

1. Create/modify models in `boards_app/models.py`
2. Run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Create serializers in `kanban_app/api/serializers.py`
4. Create views in `boards_app/api/views.py`
5. Add URL routes in `boards_app/api/urls.py`
6. Write tests in `boards_app/tests.py`
7. Run tests: `python manage.py test`

### Code Style Guide

- Use descriptive variable and function names
- Add docstrings to all classes and methods
- Keep functions under 14 lines
- Follow PEP8 naming conventions
- Use type hints where applicable

---

## License

This project is **exclusively for students of Developer Akademie** and is not released for free use or distribution.

---

## Contact & Support

For questions or issues related to this project, please contact your instructor at Developer Akademie.

---

**Happy Coding! 🚀**
