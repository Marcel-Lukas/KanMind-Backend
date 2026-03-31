# KanMind Backend

A Django REST Framework backend for a Kanban-based project management system.
It supports authentication, board collaboration, task management, and task comments.<br>
The corresponding frontend repository can be found here: 
[KanMind Frontend](https://github.com/Developer-Akademie-Backendkurs/project.KanMind)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Requirements](#-requirements)
- [Installation & Setup](#-installation--setup)
- [Database & Migrations](#-database--migrations)
- [Project Structure](#-project-structure)
- [Authentication](#-authentication)
- [API Endpoints](#-api-endpoints)
- [CORS Configuration](#-cors-configuration)
- [Troubleshooting](#-troubleshooting)
- [Helpful Documentation](#-helpful-documentation)

---

## ✨ Features

- Token-based API authentication
- Board creation and collaboration with owner/member permissions
- Task management with status, priority, assignee, reviewer, and due date
- Task comments with author tracking
- Endpoint to resolve users by email for member assignment

---

## 🛠 Tech Stack

| Component | Version |
|---|---|
| Django | 6.0.2 |
| Django REST Framework | 3.16.1 |
| django-cors-headers | 4.9.0 |
| Python | 3.12+ |
| SQLite | Development database |

---

## 📦 Requirements

- Python 3.12 or higher
- `pip`
- `venv` (recommended)

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Marcel-Lukas/KanMind-Backend
cd KanMind-Backend
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database

```bash
python manage.py migrate
python manage.py createsuperuser  # (optional) Create superuser for admin panel
```

### 5. Start development server

```bash
python manage.py runserver
```

Server URL: `http://127.0.0.1:8000/`

---

## 🗄 Database & Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

Admin panel: `http://127.0.0.1:8000/admin/`

Reset SQLite database (development only):

```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 📁 Project Structure

```text
KanMind-Backend/
├── core/                  # Django project configuration
├── auth_app/              # Registration, login, logout
├── board_app/             # Board domain + API
├── tasks_app/             # Task and task comment domain + API
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🔐 Authentication

The API uses DRF Token Authentication.

After successful registration/login, include this header in protected requests:

```http
Authorization: Token <your_token>
```

---

## 🔌 API Endpoints

Base prefix: `/api/`

### Auth

```text
POST   /api/registration/
POST   /api/login/
POST   /api/logout/              # requires token
```

### Boards

```text
GET    /api/boards/
POST   /api/boards/
GET    /api/boards/<id>/
PUT    /api/boards/<id>/
PATCH  /api/boards/<id>/
DELETE /api/boards/<id>/
GET    /api/email-check/?email=<email>
```


### Tasks

```text
GET    /api/tasks/
POST   /api/tasks/
GET    /api/tasks/<id>/
PUT    /api/tasks/<id>/
PATCH  /api/tasks/<id>/
DELETE /api/tasks/<id>/          # board owner only

GET    /api/tasks/assigned-to-me/
POST   /api/tasks/assigned-to-me/
GET    /api/tasks/reviewing/
POST   /api/tasks/reviewing/
```

### Task Comments

```text
GET    /api/tasks/<task_id>/comments/
POST   /api/tasks/<task_id>/comments/
GET    /api/tasks/<task_id>/comments/<comment_id>/
DELETE /api/tasks/<task_id>/comments/<comment_id>/
```

---

## 📝 Common Payload Fields

### Registration

```json
{
  "fullname": "Homer Simpson",
  "email": "homer-jay@simpsons.com",
  "password": "yourPassword",
  "repeated_password": "yourPassword"
}
```

### Task create/update (relevant fields)

```json
{
  "board": 1,
  "title": "Implement API docs",
  "description": "Add missing endpoint docs",
  "status": "to-do",
  "priority": "high",
  "assignee_id": 2,
  "reviewer_id": 3,
  "due_date": "2026-03-10"
}
```

---

## 🌐 CORS Configuration

Configured in `core/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
    'https://your-frontend-domain.com',  # Add/change origins
]

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]
```

---

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'django'`

**Solution**: Virtual Environment activated? Dependencies installed?

```bash
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

---

## Useful Commands

```bash
# Start server
python manage.py runserver

# Open Shell (for testing)
python manage.py shell

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Save dependencies in requirements.txt
pip freeze > requirements.txt
```

---

## 🔗 Helpful Documentation

- [Django Dokumentation](https://docs.djangoproject.com/en/6.0/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)

---

## 📧 Contact & Support

This is a very lightweight backend built with Django and should mainly be seen as a learning project. If you find any bugs or have ideas for improvements, please open an issue in the repository.

