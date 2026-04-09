# SkillSwap

> A peer-to-peer platform where users exchange skills by teaching what they know and learning what they want.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.x-green?logo=django)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.x-red)
![React](https://img.shields.io/badge/React-19.x-61DAFB?logo=react)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Default Credentials](#default-credentials)
- [API Documentation](#api-documentation)
- [Background Jobs (Celery)](#background-jobs-celery)
- [Testing](#testing)
- [Security & Performance](#security--performance)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

SkillSwap connects people who want to teach and learn from each other. No money changes hands -- just a direct exchange of skills and time.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5, Django REST Framework 3 |
| Authentication | JWT (SimpleJWT) |
| Task Queue | Celery + Redis |
| Scheduler | django-celery-beat |
| API Docs | drf-spectacular (Swagger / ReDoc) |
| Frontend | React 19, React Router, TanStack Query |
| Styling | Tailwind CSS |
| Database | SQLite (dev) / PostgreSQL (prod) |

---

## How It Works

SkillSwap is all about learning from each other. If you know something and want to share it, you can also learn something in return. It’s not about money—it’s about exchanging skills and time.

For example, let’s say User1 knows Python and User2 knows Java. User1 can send a request to User2 saying, “Hey, can you teach me Java? I’ll teach you Python in return.” Now, it’s totally up to User2 to accept or reject the request. Only if User2 agrees, the exchange will happen. It’s simple, fair, and makes learning fun!

---

## Key Features

- **User Management** -- Email-based auth, customizable profiles, profile picture uploads, availability status
- **Skill Management** -- Skill categories, proficiency tracking, active/inactive status
- **Skill Exchange** -- Exchange requests, milestone tracking, feedback and rating system
- **Advanced Features** -- Full-text search and filters, location-based user discovery, rate limiting

---

## Project Structure

```
skillswap/
├── backend/
│   ├── accounts/          # User authentication, profiles, JWT
│   ├── general/           # Shared utilities, pagination, permissions
│   ├── skillhub/          # Skill exchange, milestones, feedback
│   ├── skillswap/         # Django project configuration & Celery
│   ├── media/             # User-uploaded files
│   ├── staticfiles/       # Collected static assets
│   ├── requirements.txt
│   └── manage.py
└── frontend/
    ├── src/
    │   ├── components/    # Reusable UI components
    │   └── ...
    ├── public/
    └── package.json
```

---

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.8 or higher |
| pip | latest |
| Node.js | 16 or higher |
| npm | 8 or higher |
| Redis | any recent version (required for Celery) |

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/himanshu-suthar-simform/skillswap.git
   cd skillswap
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   # venv\Scripts\activate         # Windows
   ```

3. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Open .env and fill in your SECRET_KEY, DEBUG, ALLOWED_HOSTS, etc.
   ```

5. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Load sample data (optional, in order):**
   ```bash
   # Users and profiles
   python manage.py loaddata accounts/fixtures/users.json
   python manage.py loaddata accounts/fixtures/user_profile.json

   # Skills and exchanges
   python manage.py loaddata skillhub/fixtures/skill_categories.json
   python manage.py loaddata skillhub/fixtures/skills.json
   python manage.py loaddata skillhub/fixtures/user_skills.json
   python manage.py loaddata skillhub/fixtures/skill_exchanges.json
   python manage.py loaddata skillhub/fixtures/skill_milestones.json
   python manage.py loaddata skillhub/fixtures/skill_feedbacks.json
   ```

7. **Create the media upload directory:**
   ```bash
   mkdir -p media/profile_pictures
   ```

8. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

9. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000`.

### Frontend Setup

1. **Navigate to the frontend directory** (from the project root):
   ```bash
   cd frontend
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Set REACT_APP_API_URL=http://localhost:8000 (or your backend URL)
   ```

3. **Install Node dependencies:**
   ```bash
   npm install
   ```

4. **Start the development server:**
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`.

---

## Default Credentials

> These credentials are only available after loading the sample fixtures.

| Role | Email | Password |
|---|---|---|
| Admin | admin@admin.com | admin |
| Regular users | *(from fixtures)* | Rama@123 |

- **Admin panel:** `http://localhost:8000/admin/`

---

## API Documentation

Once the backend server is running, interactive API docs are available at:

| Interface | URL |
|---|---|
| Swagger UI | `http://localhost:8000/api/docs` |
| ReDoc | `http://localhost:8000/api/redoc` |

---

## Background Jobs (Celery)

Celery powers background tasks; django-celery-beat manages periodic schedules. Redis must be running before starting workers.

### 1. Configure environment

Add to `backend/.env`:
```env
DJANGO_ENV=dev
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 2. Run Celery locally (development)

Open two terminals from the `backend/` directory:

**Terminal 1 -- Worker:**
```bash
celery -A skillswap worker -l info
# Optional: celery -A skillswap worker -l INFO --concurrency=4 --max-tasks-per-child=1000
```

**Terminal 2 -- Beat scheduler:**
```bash
celery -A skillswap beat -l info -S django_celery_beat.schedulers:DatabaseScheduler
```

### 3. Create a periodic task (recommended)

Use the management command to register a nightly cleanup at midnight:
```bash
python manage.py create_periodic_task \
  --task-path "skillhub.tasks.cleanup.cleanup_inactive_skills_and_categories" \
  --task-name "Nightly Skill Cleanup" \
  --hour 0 \
  --minute 0
```

### 4. Alternative: Define schedule in code

Hardcode schedules in `backend/skillswap/celery.py`:
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    "cleanup-inactive-skills": {
        "task": "skillhub.tasks.cleanup.cleanup_inactive_skills_and_categories",
        "schedule": crontab(hour=0, minute=0),
    },
}
```

> **Note:** When using the database scheduler (django-celery-beat), prefer the management command (Step 3). For code-based schedules only, omit the `-S django_celery_beat.schedulers:DatabaseScheduler` flag from the beat command.

### 5. Production

Set `DJANGO_ENV=prod` and ensure all `CELERY_*` variables are configured in `.env`. Run the worker and beat processes under a process supervisor such as **systemd** or **supervisord**, adjusting the user, paths, and concurrency to match your deployment environment.

---

## Testing

SkillSwap includes comprehensive unit tests for both the `accounts` and `skillhub` apps, following Django REST Framework best practices.

All test commands below should be run from the `backend/` directory.

### Run All Tests
```bash
# Standard run
python manage.py test accounts.tests skillhub.tests

# With verbose output
python manage.py test accounts.tests skillhub.tests --verbosity=2

# In parallel (faster)
python manage.py test accounts.tests skillhub.tests --parallel
```

### Run Tests for a Specific App
```bash
python manage.py test accounts.tests
python manage.py test skillhub.tests
```

### Run a Specific Test Module, Class, or Method
```bash
# Module
python manage.py test accounts.tests.test_models
python manage.py test skillhub.tests.test_views

# Class
python manage.py test accounts.tests.test_models.UserModelTestCase

# Single method
python manage.py test accounts.tests.test_models.UserModelTestCase.test_create_user_with_valid_data
```

### Test Coverage

```bash
# 1. Run tests and collect coverage data
coverage run --source='accounts,skillhub' manage.py test accounts.tests skillhub.tests

# 2. Terminal report
coverage report

# 3. HTML report (open htmlcov/index.html in a browser)
coverage html

# 4. XML report (for CI/CD tools)
coverage xml
```

Example terminal output:
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

### Using the Test Runner Script

A convenience script (`backend/run_tests.sh`) wraps the commands above:

```bash
cd backend
chmod +x run_tests.sh   # first time only

./run_tests.sh           # run all tests with coverage
./run_tests.sh -v        # verbose output
./run_tests.sh -m test_models  # specific module
./run_tests.sh -p        # run in parallel
./run_tests.sh -f        # stop on first failure
./run_tests.sh -r        # show coverage report only
./run_tests.sh -n        # run without coverage
```

---

## Security & Performance

**Security**
- JWT-based authentication (SimpleJWT)
- Request rate limiting and throttling
- File upload validation
- Permission-based access control
- Secure password hashing

**Performance**
- Optimised database queries with select/prefetch related
- Paginated list views
- Efficient file handling via Pillow
- Database indexing on frequently queried fields

---

## Roadmap

### Frontend (In Progress)

The React frontend is approximately **40% complete**. What works today:

- Authentication context and token management
- User profile retrieval
- Exchange list display
- Basic registration and login UI

Still to be completed (~60% remaining):

- Full registration and login flow with error handling
- Skill exchange request creation and management
- Milestone tracking and feedback submission UI
- Search, filters, and location-based user discovery
- Responsive, fully interactive skill exchange interface

### Future Enhancements

- AI-based skill matching and recommendations
- Gamification (badges, points, achievements)
- Group-based learning and community events
- Payment integration for premium mentorship
- Video call or meeting integration
- Leaderboard (top teachers and learners of the week)

---

## Contributing

Contributions are welcome! Please open an issue to discuss your proposed change before submitting a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## License

This project is licensed under the [MIT License](LICENSE).
