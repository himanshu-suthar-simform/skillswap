# SkillSwap

A peer-to-peer platform where users exchange skills by teaching what they know and learning what they want.

## Overview

SkillSwap is a dynamic platform that facilitates peer-to-peer skill exchange and learning. Users can share their expertise, learn new skills, and engage in mutually beneficial learning relationships.

### Key Features

- **User Management**
  - Email-based authentication
  - Profile management with customizable details
  - Profile picture upload support
  - User availability status

- **Skill Management**
  - Skill categories
  - User skill registration
  - Skill proficiency tracking
  - Active/Inactive skill status

- **Skill Exchange**
  - Skill exchange requests
  - Exchange milestone tracking
  - Feedback and rating system
  - Exchange status management

- **Advanced Features**
  - Search and filter capabilities
  - User availability tracking
  - Location-based user search
  - Comprehensive feedback system

## Project Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv or venv

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/himanshu-suthar-simform/skillswap.git
   cd skillswap
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

6. Load initial data (fixtures) in the following order:
   ```bash
   # Load users and profiles first
   python manage.py loaddata accounts/fixtures/users.json
   python manage.py loaddata accounts/fixtures/user_profile.json

   # Then load skill-related data
   python manage.py loaddata skillhub/fixtures/skill_categories.json
   python manage.py loaddata skillhub/fixtures/skills.json
   python manage.py loaddata skillhub/fixtures/user_skills.json
   python manage.py loaddata skillhub/fixtures/skill_exchanges.json
   python manage.py loaddata skillhub/fixtures/skill_milestones.json
   python manage.py loaddata skillhub/fixtures/skill_feedbacks.json
   ```

7. Create media directory for uploads:
    ```bash
    mkdir -p media/profile_pictures
    ```

8. Collect static files for local development purpose
    ```bash
    python manage.py collectstatic
    ```

9.  Run the development server:
    ```bash
    python manage.py runserver
    ```

### Default Credentials

- **Admin User**
  - Email: admin@admin.com
  - Password: admin
  - Access admin panel at: http://localhost:8000/admin/

- **Regular Users**
  - All users from fixtures have password: Rama@123

### API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure
```
backend/
├── accounts/          # User management
├── general/           # Common utilities
├── skillhub/          # Skill exchange features
├── skillswap/         # Project configuration
├── media/            # User uploads
└── staticfiles/      # Static files
```

### Key Components

1. **Accounts App**
   - User authentication and registration
   - Profile management with picture upload
   - JWT token handling
   - User search and filtering

2. **SkillHub App**
   - Skill categories and management
   - Skill exchange coordination
   - Progress tracking with milestones
   - Feedback and rating system

3. **General App**
   - Common utilities and helpers
   - Custom pagination
   - Permission classes
   - Rate limiting and throttling

## Security Features

- JWT-based authentication
- Request rate limiting
- File upload validation
- Permission-based access control
- Secure password handling

## Performance Features

- Optimized database queries
- Efficient file handling
- Paginated list views
- Optimized search functionality
- Database indexing

## Testing

SkillSwap includes comprehensive unit tests for both the accounts and skillhub apps, following Django REST Framework best practices.

### Running Tests

#### Run All Tests
```bash
cd backend

# Run all tests for both apps
python manage.py test accounts.tests skillhub.tests

# Run with verbose output
python manage.py test accounts.tests skillhub.tests --verbosity=2

# Run tests in parallel (faster)
python manage.py test accounts.tests skillhub.tests --parallel
```

#### Run Tests for Specific App
```bash
# Accounts app tests
python manage.py test accounts.tests

# SkillHub app tests
python manage.py test skillhub.tests
```

#### Run Specific Test Module
```bash
# Model tests
python manage.py test accounts.tests.test_models
python manage.py test skillhub.tests.test_models

# Serializer tests
python manage.py test accounts.tests.test_serializers
python manage.py test skillhub.tests.test_serializers

# View tests
python manage.py test accounts.tests.test_views
python manage.py test skillhub.tests.test_views
```

#### Run Specific Test Class
```bash
python manage.py test accounts.tests.test_models.UserModelTestCase
python manage.py test skillhub.tests.test_models.SkillCategoryModelTestCase
```

#### Run Specific Test Method
```bash
python manage.py test accounts.tests.test_models.UserModelTestCase.test_create_user_with_valid_data
```

### Test Coverage

#### Generate Coverage Report

1. **Install coverage.py** (if not already installed):
   ```bash
   pip install coverage
   ```

2. **Run tests with coverage**:
   ```bash
   # Run tests and collect coverage data
   coverage run --source='accounts,skillhub' manage.py test accounts.tests skillhub.tests
   ```

3. **View coverage report in terminal**:
   ```bash
   coverage report
   ```

   Example output:
   ```
   Name                              Stmts   Miss  Cover
   -----------------------------------------------------
   accounts/models.py                   73      3    96%
   accounts/serializers.py             156      8    95%
   accounts/views.py                   123      7    94%
   skillhub/models.py                  145      6    96%
   skillhub/serializers.py             234     12    95%
   skillhub/views.py                   289     15    95%
   -----------------------------------------------------
   TOTAL                              1020     51    95%
   ```

4. **Generate HTML coverage report**:
   ```bash
   coverage html
   ```

   This creates an `htmlcov/` directory. Open `htmlcov/index.html` in your browser to view the detailed coverage report with highlighted code.

5. **Generate XML coverage report** (for CI/CD):
   ```bash
   coverage xml
   ```

   This creates a `coverage.xml` file compatible with CI/CD tools like Jenkins, GitLab CI, GitHub Actions, etc.

#### Using the Test Runner Script

A convenient test runner script is provided:

```bash
# Make the script executable (first time only)
chmod +x run_tests.sh

# Run all tests with coverage
./run_tests.sh

# Run with verbose output
./run_tests.sh -v

# Run specific module
./run_tests.sh -m test_models

# Run in parallel
./run_tests.sh -p

# Stop on first failure
./run_tests.sh -f

# Show coverage report only (without running tests)
./run_tests.sh -r

# Run without coverage
./run_tests.sh -n
```

## Background Jobs (Celery)

Celery powers background jobs and django-celery-beat manages periodic schedules.

Prerequisites assumed: Redis is running and reachable by your app.

### 1. Configure environment

Add the following to backend/.env (adjust if needed):
```env
DJANGO_ENV=dev  # or prod/staging
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

Ensure migrations are applied (includes django_celery_beat tables):
```bash
cd backend
python manage.py migrate
```

### 2. Run Celery locally (development)

Use two terminals from the backend directory.

- Terminal 1: Celery worker
  ```bash
  cd backend
  celery -A skillswap worker -l info
  # Optional tuning
  # celery -A skillswap worker -l INFO --concurrency=4 --max-tasks-per-child=1000
  ```

- Terminal 2: Celery beat (database scheduler)
  ```bash
  cd backend
  celery -A skillswap beat -l info -S django_celery_beat.schedulers:DatabaseScheduler
  ```

### 3. Create a periodic task (recommended)

Create a nightly cleanup at 00:00 using the management command:
```bash
cd backend
python manage.py create_periodic_task \
  --task-path "skillhub.tasks.cleanup.cleanup_inactive_skills_and_categories" \
  --task-name "Nightly Skill Cleanup" \
  --hour 0 \
  --minute 0
```

### 4. Alternative: Define schedule in code

You can hardcode schedules in backend/skillswap/celery.py:
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    "cleanup-inactive-skills": {
        "task": "skillhub.tasks.cleanup.cleanup_inactive_skills_and_categories",
        "schedule": crontab(hour=0, minute=0),
    },
}
```

Note: When using django-celery-beat (database scheduler), prefer the management command (Step 3). If you use code-based schedules only, run beat without the database scheduler flag.

### 5. Production-grade run

- Set environment appropriately (DJANGO_ENV=prod) and ensure .env includes the CELERY_* settings.
- Run worker and beat under a supervisor (systemd example below). Adjust paths, user, and concurrency.


## Frontend Development

The frontend implementation is currently in progress.
It can be developed in the future, following the same modular structure and API-driven approach of the backend.
