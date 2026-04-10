# 📚 SkillSwap — Complete Project Documentation

> **A peer-to-peer skill exchange platform** where people teach what they know and learn what they want — no money involved, just a fair exchange of knowledge and time.

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Who Is It For?](#2-who-is-it-for)
3. [How It Works (Simple Version)](#3-how-it-works-simple-version)
4. [Key Features](#4-key-features)
5. [Technology Stack](#5-technology-stack)
6. [Project Structure](#6-project-structure)
7. [Setup & Installation Guide](#7-setup--installation-guide)
   - [Prerequisites](#prerequisites)
   - [Step 1 — Clone the Repository](#step-1--clone-the-repository)
   - [Step 2 — Backend Setup](#step-2--backend-setup)
   - [Step 3 — Frontend Setup](#step-3--frontend-setup)
8. [Running the Application](#8-running-the-application)
9. [Environment Variables Reference](#9-environment-variables-reference)
10. [Default Credentials & Sample Data](#10-default-credentials--sample-data)
11. [Application Pages & User Guide](#11-application-pages--user-guide)
12. [API Documentation](#12-api-documentation)
    - [Authentication Endpoints](#authentication-endpoints)
    - [User Endpoints](#user-endpoints)
    - [Skill Category Endpoints](#skill-category-endpoints)
    - [Skill Endpoints](#skill-endpoints)
    - [Teaching Skill Endpoints](#teaching-skill-endpoints)
    - [Skill Exchange Endpoints](#skill-exchange-endpoints)
    - [Feedback Endpoints](#feedback-endpoints)
13. [Background Jobs (Celery)](#13-background-jobs-celery)
14. [Testing Guide](#14-testing-guide)
15. [Security & Performance](#15-security--performance)
16. [Roadmap](#16-roadmap)
17. [Contributing](#17-contributing)
18. [License](#18-license)

---

## 1. Project Overview

**SkillSwap** is an online platform that connects people who want to share their knowledge with people who want to learn. Think of it like a barter system for skills — instead of paying money, you exchange your expertise.

For example:
- 🧑‍💻 **Alice** knows Python programming and wants to learn guitar.
- 🎸 **Bob** plays guitar and wants to learn Python.
- On SkillSwap, Alice and Bob can find each other, agree on an exchange, and both walk away having learned something new — for free.

The platform handles everything: finding matches, managing exchange requests, tracking learning progress through milestones, and collecting feedback after each exchange is complete.

---

## 2. Who Is It For?

SkillSwap is designed for **anyone who has a skill to share and something they want to learn**. This includes:

| Type of User | What they get |
|---|---|
| 🎓 **Students** | Learn new skills from experienced people without paying tuition |
| 👩‍💼 **Professionals** | Share expertise and pick up complementary skills |
| 🌍 **Hobbyists** | Connect with others who share interests or want to learn yours |
| 🏫 **Teachers & Tutors** | Find peer learning opportunities in areas outside their specialty |

---

## 3. How It Works (Simple Version)

SkillSwap works in 4 easy steps:

```
1. 📝 Sign Up  →  Create an account and build your profile

2. 🎯 List a Skill  →  Add skills you can teach (e.g., "Guitar", "Python")

3. 🔍 Browse & Request  →  Find someone teaching what you want to learn
                           and send them an exchange request

4. ✅ Exchange & Learn  →  The teacher accepts, you both learn, and leave feedback
```

**Exchange flow in detail:**

```
Learner sends request
        ↓
Teacher reviews and ACCEPTS or DECLINES
        ↓
Exchange goes IN PROGRESS (learning sessions happen)
        ↓
Exchange marked COMPLETED
        ↓
Learner submits feedback and rating
```

> **Important:** An exchange only happens when the teacher explicitly accepts. No one is forced into any exchange.

---

## 4. Key Features

### 👤 User Management
- ✅ Email-based registration and login
- ✅ Customizable user profiles with photos
- ✅ Availability status (set yourself as available or busy)
- ✅ Location and timezone settings for scheduling

### 🧠 Skill Management
- ✅ Organized skill categories (e.g., Programming, Music, Languages)
- ✅ Proficiency levels: Beginner → Intermediate → Advanced → Expert
- ✅ Skill milestones — break learning into clear checkpoints
- ✅ Estimated duration per skill
- ✅ Maximum students per teacher setting

### 🔄 Skill Exchange System
- ✅ Send, accept, and manage exchange requests
- ✅ Exchange statuses: Pending → Accepted → In Progress → Completed / Cancelled
- ✅ Learning goals and notes for each exchange
- ✅ Feedback and star ratings after completion

### 🔍 Discovery & Search
- ✅ Full-text search across skills and users
- ✅ Filter by category, proficiency level, experience, and more
- ✅ Location-based user discovery

### 🔒 Security
- ✅ JWT (JSON Web Token) authentication — industry-standard secure login
- ✅ Rate limiting to prevent abuse
- ✅ File upload validation
- ✅ Role-based permissions (Admin vs. regular users)

### ⚙️ Background Processing
- ✅ Automated nightly cleanup of inactive skills and categories
- ✅ Scheduled task management via Celery and Redis

---

## 5. Technology Stack

> **Don't know what these are?** Think of the "stack" as the collection of tools the developers used to build SkillSwap.

| Layer | Technology | What it does |
|---|---|---|
| **Backend (Server)** | Python + Django 5 | Handles all the logic, data storage, and API |
| **REST API** | Django REST Framework 3 | Allows the frontend and backend to talk to each other |
| **Authentication** | SimpleJWT | Securely logs users in/out using tokens |
| **Task Queue** | Celery + Redis | Runs background jobs (like cleanup) without slowing down the app |
| **Scheduler** | django-celery-beat | Runs tasks on a schedule (e.g., every night at midnight) |
| **API Docs** | drf-spectacular | Auto-generates interactive API documentation |
| **Frontend (Browser)** | React 19 | The visual interface users interact with |
| **Routing** | React Router 7 | Handles navigation between pages |
| **Data Fetching** | TanStack Query 5 | Efficiently loads and caches data from the API |
| **Forms** | React Hook Form + Yup | Handles form inputs and validation |
| **Styling** | Tailwind CSS 3 | Makes the interface look good |
| **HTTP Client** | Axios | Sends requests from the browser to the server |
| **Notifications** | React Toastify | Shows pop-up notifications to users |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Stores all application data |

---

## 6. Project Structure

Below is a map of the most important files and folders:

```
skillswap/
├── 📄 README.md              ← Quick-start overview
├── 📄 docs.md                ← This file — full documentation
├── 📄 guide.md               ← Additional guides
│
├── 🗂️ backend/               ← All server-side code (Python/Django)
│   ├── manage.py             ← Django's command-line tool
│   ├── requirements.txt      ← List of Python packages needed
│   ├── .env.example          ← Template for environment variables
│   ├── pytest.ini            ← Test configuration
│   ├── run_tests.sh          ← Convenience script for running tests
│   │
│   ├── 📁 accounts/          ← User registration, login, profiles
│   │   ├── models.py         ← User and Profile data definitions
│   │   ├── views.py          ← API endpoints for accounts
│   │   ├── serializers.py    ← Data formatting/validation
│   │   ├── urls.py           ← Account-related URL routes
│   │   ├── fixtures/         ← Sample user data for testing
│   │   └── tests/            ← Unit and integration tests
│   │
│   ├── 📁 skillhub/          ← Core skill exchange logic
│   │   ├── models.py         ← Skill, Exchange, Feedback data definitions
│   │   ├── views.py          ← API endpoints for skills and exchanges
│   │   ├── serializers.py    ← Data formatting/validation
│   │   ├── filters.py        ← Search and filter logic
│   │   ├── urls.py           ← Skill-related URL routes
│   │   ├── fixtures/         ← Sample skill/exchange data for testing
│   │   ├── tasks/            ← Background cleanup tasks
│   │   └── tests/            ← Unit and integration tests
│   │
│   ├── 📁 general/           ← Shared utilities used across the app
│   │   ├── pagination.py     ← Controls how many results appear per page
│   │   ├── permissions.py    ← Who can do what (access control)
│   │   └── throttling.py     ← Rate limits to prevent abuse
│   │
│   └── 📁 skillswap/         ← Project-wide Django configuration
│       ├── settings/
│       │   ├── base.py       ← Common settings for all environments
│       │   ├── dev.py        ← Development-only settings
│       │   ├── staging.py    ← Staging environment settings
│       │   └── prod.py       ← Production settings
│       ├── urls.py           ← Main URL routing file
│       ├── celery.py         ← Background task configuration
│       └── healthcheck.py    ← Server health check endpoint
│
└── 🗂️ frontend/              ← All browser-side code (React)
    ├── package.json          ← List of JavaScript packages needed
    ├── .env.example          ← Template for frontend environment variables
    ├── tailwind.config.js    ← Styling configuration
    │
    └── 📁 src/
        ├── App.js            ← Root application component
        ├── index.js          ← Entry point
        │
        ├── 📁 api/           ← Functions that talk to the backend
        │   ├── api.js        ← Base Axios configuration
        │   ├── auth.js       ← Login/register API calls
        │   ├── user.js       ← User profile API calls
        │   ├── skills.js     ← Skill-related API calls
        │   └── exchanges.js  ← Exchange-related API calls
        │
        ├── 📁 context/       ← App-wide state management
        │   └── AuthProvider.jsx  ← Handles authentication state
        │
        ├── 📁 hooks/         ← Reusable logic hooks
        │   └── useAuth.js    ← Hook for accessing auth state
        │
        ├── 📁 routes/        ← Page routing configuration
        │   └── AppRouter.jsx ← Defines all page routes
        │
        └── 📁 pages/         ← Individual page components
            ├── Login.jsx
            ├── Register.jsx
            ├── Dashboard.jsx
            ├── Profile.jsx
            ├── UserProfile.jsx
            ├── UserList.jsx
            ├── TeachingSkills.jsx
            ├── TeachingSkillDetail.jsx
            ├── ManageRequests.jsx
            ├── RequestToLearnModal.jsx
            └── ExchangeDetailModal.jsx
```

---

## 7. Setup & Installation Guide

> **First time setting up a project like this?** Follow the steps carefully in order. Each step builds on the previous one.

### Prerequisites

Before you start, make sure you have these tools installed on your computer:

| Tool | Minimum Version | How to check | Download |
|---|---|---|---|
| **Python** | 3.8+ | `python --version` | [python.org](https://www.python.org/downloads/) |
| **pip** | latest | `pip --version` | Comes with Python |
| **Node.js** | 16+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| **npm** | 8+ | `npm --version` | Comes with Node.js |
| **Redis** | any recent | `redis-cli ping` | [redis.io](https://redis.io/download/) |
| **Git** | any | `git --version` | [git-scm.com](https://git-scm.com/) |

> 💡 **What is Redis?** Redis is a fast, in-memory data store used by SkillSwap to run background tasks (like nightly cleanup). It must be installed and running before starting the backend.

---

### Step 1 — Clone the Repository

"Cloning" means downloading the project code to your computer.

```bash
git clone https://github.com/himanshu-suthar-simform/skillswap.git
cd skillswap
```

---

### Step 2 — Backend Setup

The backend is the "brain" of SkillSwap — it handles all data, logic, and security.

#### 2a. Create a Virtual Environment

A virtual environment keeps SkillSwap's Python packages isolated from the rest of your system.

```bash
# Create the virtual environment
python -m venv venv

# Activate it (choose the command for your operating system)
source venv/bin/activate        # ✅ macOS / Linux
venv\Scripts\activate           # ✅ Windows (Command Prompt)
```

> 💡 You'll know it's active when you see `(venv)` at the start of your terminal prompt.

#### 2b. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs all the Python packages the backend needs (Django, Celery, JWT, etc.).

#### 2c. Set Up Environment Variables

Environment variables are secret configuration values that should never be shared publicly (like your secret key or database password).

```bash
cp .env.example .env
```

Now open the newly created `.env` file in a text editor and fill in the values. See the [Environment Variables Reference](#9-environment-variables-reference) section below for details on each value.

**Minimum required values for development:**

```env
SECRET_KEY=any-long-random-string-you-make-up
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_ENV=dev
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

#### 2d. Apply Database Migrations

"Migrations" create the database tables needed by the application.

```bash
python manage.py migrate
```

#### 2e. Create the Media Upload Directory

This folder stores user-uploaded profile pictures.

```bash
mkdir -p media/profile_pictures
```

#### 2f. (Optional) Load Sample Data

Loading sample data gives you test users, skills, and exchanges to explore right away.

```bash
# Load in this exact order — order matters!
python manage.py loaddata accounts/fixtures/users.json
python manage.py loaddata accounts/fixtures/user_profile.json
python manage.py loaddata skillhub/fixtures/skill_categories.json
python manage.py loaddata skillhub/fixtures/skills.json
python manage.py loaddata skillhub/fixtures/user_skills.json
python manage.py loaddata skillhub/fixtures/skill_exchanges.json
python manage.py loaddata skillhub/fixtures/skill_milestones.json
python manage.py loaddata skillhub/fixtures/skill_feedbacks.json
```

#### 2g. Create an Admin User (if not using sample data)

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin email and password.

#### 2h. Collect Static Files

```bash
python manage.py collectstatic
```

---

### Step 3 — Frontend Setup

The frontend is the visual interface that users see in their browser.

#### 3a. Navigate to the Frontend Directory

```bash
# From the project root (skillswap/)
cd frontend
```

#### 3b. Set Up Environment Variables

```bash
cp .env.example .env
```

The frontend only needs one environment variable — the URL of the backend API:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

#### 3c. Install JavaScript Dependencies

```bash
npm install
```

This may take a minute while it downloads all the JavaScript packages listed in `package.json`.

---

## 8. Running the Application

You'll need **three separate terminal windows** running simultaneously.

### Terminal 1 — Backend Server

```bash
cd backend
source venv/bin/activate   # activate virtual environment
python manage.py runserver
```

✅ Backend is ready at: **http://localhost:8000**

### Terminal 2 — Frontend Server

```bash
cd frontend
npm start
```

✅ Frontend is ready at: **http://localhost:3000**

### Terminal 3 — Background Tasks (Celery Worker)

> Only needed if you want background jobs (like nightly cleanup) to run.

```bash
cd backend
source venv/bin/activate
celery -A skillswap worker -l info
```

### (Optional) Terminal 4 — Celery Beat Scheduler

> Only needed if you want **scheduled** tasks (tasks that run automatically on a timer).

```bash
cd backend
source venv/bin/activate
celery -A skillswap beat -l info -S django_celery_beat.schedulers:DatabaseScheduler
```

### Quick Reference

| Service | URL | Terminal Command |
|---|---|---|
| 🌐 Frontend App | http://localhost:3000 | `npm start` (from `frontend/`) |
| 🔌 Backend API | http://localhost:8000 | `python manage.py runserver` (from `backend/`) |
| 📖 API Docs (Swagger) | http://localhost:8000/api/docs | *(auto, backend must be running)* |
| 📖 API Docs (ReDoc) | http://localhost:8000/api/redoc | *(auto, backend must be running)* |
| 🛠️ Admin Panel | http://localhost:8000/admin | *(auto, backend must be running)* |
| 💓 Health Check | http://localhost:8000/status | *(auto, backend must be running)* |

---

## 9. Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Example Value | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ Yes | `s3cr3t-key-abc123...` | Django's cryptographic secret key. Use a long, random string. **Never share this.** |
| `DEBUG` | ✅ Yes | `True` | Set to `True` in development, `False` in production. |
| `ALLOWED_HOSTS` | ✅ Yes | `localhost,127.0.0.1` | Comma-separated list of hostnames the server accepts requests from. |
| `DJANGO_ENV` | ✅ Yes | `dev` | Controls which settings file to use. Options: `dev`, `staging`, `prod`. |
| `NUM_PROXIES` | ❌ Optional | `1` | Number of trusted reverse proxies (used for accurate IP detection). |
| `KNOWN_PROXIES` | ❌ Optional | `127.0.0.1` | IP addresses of trusted proxies. |
| `CELERY_BROKER_URL` | ✅ Yes* | `redis://localhost:6379/0` | Redis URL for Celery task queue. *Required if using background tasks. |
| `CELERY_RESULT_BACKEND` | ✅ Yes* | `redis://localhost:6379/1` | Redis URL for storing task results. *Required if using background tasks. |

> 💡 **What is a SECRET_KEY?** It's like a master password Django uses internally for security features. Generate one at: https://djecrety.ir/

### Frontend (`frontend/.env`)

| Variable | Required | Example Value | Description |
|---|---|---|---|
| `REACT_APP_API_URL` | ✅ Yes | `http://localhost:8000/api/v1` | The base URL of the backend API. All API calls are made to this address. |

---

## 10. Default Credentials & Sample Data

> ⚠️ These credentials are only available **after loading the sample fixtures** (Step 2f above).

### Login Credentials

| Role | Email | Password | Access Level |
|---|---|---|---|
| 🛡️ Admin | `admin@admin.com` | `admin` | Full access including admin panel |
| 👤 Regular User | `test@gmail.com` | `Rama@123` | Standard user access |
| 👤 Regular User | `test1@gmail.com` | `Rama@123` | Standard user access |
| 👤 Regular User | `test2@gmail.com` | `Rama@123` | Standard user access |

### Admin Panel

Access the Django admin panel at: **http://localhost:8000/admin/**

The admin panel lets you:
- View and manage all users
- View and manage all skills and exchanges
- Activate or deactivate user accounts
- Monitor background task schedules

---

## 11. Application Pages & User Guide

### 🔐 Registration & Login

**Register (`/register`)**
- Create a new account by providing your name, email, username, and password.
- After registering, your account needs to be **activated by an admin** before you can log in.

**Login (`/login`)**
- Log in with your email address and password.
- A secure JWT token is issued and stored in your browser session.

---

### 🏠 Dashboard (`/dashboard`)

Your personal home page after logging in. Shows:
- A summary of your active exchanges
- Quick links to browse skills and manage requests

---

### 👤 Profile (`/profile`)

View and edit your personal profile:
- Update your bio, location, and timezone
- Upload a profile picture
- Set your availability status (Available / Busy)
- Change language preferences

---

### 👥 User List (`/users`)

Browse all registered users on the platform. Use this to:
- Discover potential skill exchange partners
- Filter users by location or availability
- Click on a user to see their full profile and the skills they offer

---

### 🧑‍🏫 Teaching Skills (`/teaching-skills`)

Browse all skills being offered by teachers. You can:
- Filter by category, proficiency level, and experience
- Search by skill name
- Click a skill to see full details and milestones

**Skill Detail Page** shows:
- Skill description and learning outcomes
- Teaching methods and prerequisites
- Estimated duration and milestones
- Teacher's average rating and success rate
- A button to **Request to Learn** (sends an exchange request)

---

### 📬 Manage Requests (`/manage-requests`)

Manage your incoming and outgoing exchange requests:
- **Incoming requests** — Requests from learners who want to learn from you. Accept or decline them.
- **Outgoing requests** — Requests you've sent to others. Track their status.

**Exchange statuses explained:**

| Status | Meaning |
|---|---|
| 🟡 **Pending** | Waiting for the teacher to respond |
| 🟢 **Accepted** | Teacher said yes — learning can begin! |
| 🔵 **In Progress** | Learning sessions are actively happening |
| ✅ **Completed** | Exchange finished — learner can now leave feedback |
| ❌ **Cancelled** | Exchange was cancelled by either party |

---

### ⭐ Leaving Feedback

After an exchange is completed:
1. The **learner** submits a rating (0–5 stars) and written comment
2. They indicate whether they'd **recommend** this teacher
3. Feedback can be updated within **72 hours** of submission

---

## 12. API Documentation

> 💡 **Interactive documentation** is available while the backend server is running:
> - **Swagger UI** (try it live): http://localhost:8000/api/docs
> - **ReDoc** (clean reference): http://localhost:8000/api/redoc

All API endpoints are prefixed with `/api/v1/`.

Authentication uses **JWT Bearer tokens**. Include the token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

---

### Authentication Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/v1/accounts/auth/register/` | ❌ No | Create a new user account |
| `POST` | `/api/v1/accounts/auth/token/` | ❌ No | Log in — returns access & refresh tokens |
| `POST` | `/api/v1/accounts/auth/token/refresh/` | ❌ No | Exchange a refresh token for a new access token |
| `POST` | `/api/v1/accounts/auth/token/verify/` | ❌ No | Check if a token is valid |

**Register — Example Request:**
```json
POST /api/v1/accounts/auth/register/
{
  "email": "alice@example.com",
  "username": "alice",
  "first_name": "Alice",
  "last_name": "Smith",
  "password": "SecurePass123!"
}
```

**Login — Example Request:**
```json
POST /api/v1/accounts/auth/token/
{
  "email": "alice@example.com",
  "password": "SecurePass123!"
}
```

**Login — Example Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

> ⏱️ **Rate limit on login:** Max **3 attempts per minute** per IP address to prevent brute force attacks.

---

### User Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/v1/accounts/users/` | ✅ Yes | List all users (paginated) |
| `GET` | `/api/v1/accounts/users/{id}/` | ✅ Yes | Get a specific user's details |
| `GET` | `/api/v1/accounts/users/me/` | ✅ Yes | Get the currently logged-in user's details |
| `PATCH` | `/api/v1/accounts/users/me/profile/` | ✅ Yes | Update your own profile |

**Update Profile — Example Request:**
```json
PATCH /api/v1/accounts/users/me/profile/
{
  "bio": "Python developer who loves teaching",
  "location": "San Francisco, USA",
  "timezone": "America/Los_Angeles",
  "is_available": true
}
```

---

### Skill Category Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/v1/skillhub/categories/` | ✅ Yes | List all skill categories |
| `POST` | `/api/v1/skillhub/categories/` | ✅ Admin | Create a new category |
| `GET` | `/api/v1/skillhub/categories/{id}/` | ✅ Yes | Get a specific category |
| `PUT/PATCH` | `/api/v1/skillhub/categories/{id}/` | ✅ Admin | Update a category |
| `DELETE` | `/api/v1/skillhub/categories/{id}/` | ✅ Admin | Delete a category |

**Available Filters for Categories:**

| Filter | Type | Example | Description |
|---|---|---|---|
| `name` | string | `?name=prog` | Partial name match (case-insensitive) |
| `is_active` | boolean | `?is_active=true` | Filter by active status |
| `has_skills` | boolean | `?has_skills=true` | Only categories that have active skills |
| `created_after` | datetime | `?created_after=2024-01-01` | Created on or after this date |
| `created_before` | datetime | `?created_before=2024-12-31` | Created on or before this date |

---

### Skill Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/v1/skillhub/skills/` | ✅ Yes | List all skills |
| `POST` | `/api/v1/skillhub/skills/` | ✅ Admin | Create a new skill |
| `GET` | `/api/v1/skillhub/skills/{id}/` | ✅ Yes | Get a specific skill |
| `PUT/PATCH` | `/api/v1/skillhub/skills/{id}/` | ✅ Admin | Update a skill |
| `DELETE` | `/api/v1/skillhub/skills/{id}/` | ✅ Admin | Delete a skill |

**Available Filters for Skills:**

| Filter | Type | Example | Description |
|---|---|---|---|
| `name` | string | `?name=python` | Partial name match |
| `category` | integer | `?category=3` | Filter by category ID |
| `category_name` | string | `?category_name=prog` | Filter by category name (partial) |
| `is_active` | boolean | `?is_active=true` | Filter by active status |
| `has_teachers` | boolean | `?has_teachers=true` | Only skills with active teachers |
| `min_teachers` | integer | `?min_teachers=2` | Skills with at least N teachers |

---

### Teaching Skill Endpoints

A "teaching skill" is a skill that a specific user is offering to teach.

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/v1/skillhub/teaching-skills/` | ✅ Yes | List all teaching skill offerings |
| `POST` | `/api/v1/skillhub/teaching-skills/` | ✅ Yes | Offer to teach a skill |
| `GET` | `/api/v1/skillhub/teaching-skills/{id}/` | ✅ Yes | Get details of a teaching skill |
| `PUT/PATCH` | `/api/v1/skillhub/teaching-skills/{id}/` | ✅ Owner/Admin | Update a teaching skill |
| `DELETE` | `/api/v1/skillhub/teaching-skills/{id}/` | ✅ Owner/Admin | Remove a teaching skill |

**Create Teaching Skill — Example Request:**
```json
POST /api/v1/skillhub/teaching-skills/
{
  "skill": 5,
  "proficiency_level": "ADVANCED",
  "years_of_experience": 4,
  "learning_outcomes": "You will be able to build REST APIs with Django",
  "teaching_methods": "Hands-on coding exercises and code reviews",
  "estimated_duration": 20,
  "duration_type": "HOURS",
  "max_students": 2,
  "available_time_slots": "Weekends, 9am-12pm UTC"
}
```

**Proficiency Levels:**

| Value | Label |
|---|---|
| `BEGINNER` | Beginner |
| `INTERMEDIATE` | Intermediate |
| `ADVANCED` | Advanced |
| `EXPERT` | Expert |

**Duration Types:**

| Value | Meaning |
|---|---|
| `HOURS` | Estimated in hours |
| `DAYS` | Estimated in days |
| `WEEKS` | Estimated in weeks |
| `MONTHS` | Estimated in months |

**Available Filters for Teaching Skills:**

| Filter | Example | Description |
|---|---|---|
| `skill` | `?skill=5` | Filter by skill ID |
| `category` | `?category=2` | Filter by category ID |
| `user` | `?user=7` | Filter by teacher user ID |
| `is_active` | `?is_active=true` | Only active offerings |
| `proficiency_level` | `?proficiency_level=ADVANCED` | Exact proficiency match |
| `min_experience` | `?min_experience=2` | Minimum years of experience |
| `has_students` | `?has_students=true` | Teachers who already have students |

> ⏱️ **Rate limit on creation:** Max **10 per hour** and **100 per day** per user.

---

### Skill Exchange Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/v1/skillhub/exchanges/` | ✅ Yes | List your exchanges |
| `POST` | `/api/v1/skillhub/exchanges/` | ✅ Yes | Send a new exchange request |
| `GET` | `/api/v1/skillhub/exchanges/{id}/` | ✅ Yes | Get exchange details |
| `PATCH` | `/api/v1/skillhub/exchanges/{id}/` | ✅ Owner/Admin | Update exchange (e.g., accept/decline) |

**Send Exchange Request — Example Request:**
```json
POST /api/v1/skillhub/exchanges/
{
  "user_skill": 12,
  "learning_goals": "I want to build my first Django project within 3 weeks",
  "availability": "Evenings (6pm-9pm UTC), Monday to Friday",
  "proposed_duration": 15,
  "notes": "I already know Python basics, so I can jump to intermediate topics"
}
```

**Exchange Statuses:**

| Status | Who Can Set | Description |
|---|---|---|
| `PENDING` | System (auto) | Initial state when request is sent |
| `ACCEPTED` | Teacher | Teacher agrees to the exchange |
| `IN_PROGRESS` | Teacher | Learning sessions have begun |
| `COMPLETED` | Teacher | Learning is done |
| `CANCELLED` | Either party | Exchange is called off |

---

### Feedback Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/v1/skillhub/feedback/` | ✅ Yes | List feedback |
| `POST` | `/api/v1/skillhub/feedback/` | ✅ Yes (learner only) | Submit feedback for a completed exchange |
| `GET` | `/api/v1/skillhub/feedback/{id}/` | ✅ Yes | Get specific feedback |
| `PATCH` | `/api/v1/skillhub/feedback/{id}/` | ✅ Owner/Admin | Update feedback (within 72 hours) |

**Submit Feedback — Example Request:**
```json
POST /api/v1/skillhub/feedback/
{
  "exchange": 8,
  "rating": 4.50,
  "comment": "Great teacher! Very patient and explains concepts clearly.",
  "is_recommended": true
}
```

> 💡 **Rating format:** Ratings are decimal values between **0.00 and 5.00** (e.g., `4.50`, `3.75`, `5.00`). Two decimal places are supported.

> ⏱️ **Rate limit on feedback:** Max **5 per hour** and **30 per day** per user.
>
> 🕐 **Edit window:** Feedback can only be updated within **72 hours** of submission.

---

### Pagination

All list endpoints return paginated results. The response format is:

```json
{
  "count": 42,
  "total_pages": 5,
  "current_page": 1,
  "next": "http://localhost:8000/api/v1/skillhub/skills/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

Control pagination with query parameters:
- `?page=2` — Go to page 2
- `?page_size=20` — Show 20 results per page (default: 10, max: 100)

---

### Health Check

```
GET /status/
```

Returns a `200 OK` with a simple status message. Used to verify the server is running.

---

## 13. Background Jobs (Celery)

SkillSwap uses **Celery** to run tasks in the background, so they don't slow down the main application.

> 💡 **What is Celery?** Think of it like a to-do list manager that runs tasks automatically, either triggered by actions or on a schedule. **Redis** is the "bulletin board" where tasks are posted and picked up by workers.

### Available Tasks

| Task | Schedule | Description |
|---|---|---|
| `skillhub.tasks.cleanup.cleanup_inactive_skills_and_categories` | Nightly at midnight | Automatically cleans up skills and categories that have been inactive for a long time |

### Setting Up a Scheduled Task

After starting the Celery worker and beat scheduler, register a scheduled task with:

```bash
python manage.py create_periodic_task \
  --task-path "skillhub.tasks.cleanup.cleanup_inactive_skills_and_categories" \
  --task-name "Nightly Skill Cleanup" \
  --hour 0 \
  --minute 0
```

### Rate Limiting Summary

| Action | Limit |
|---|---|
| Login attempts | 3 per minute per IP |
| Skill creation | 10 per hour / 100 per day per user |
| Feedback submission | 5 per hour / 30 per day per user |

---

## 14. Testing Guide

SkillSwap has a comprehensive test suite covering models, serializers, views, and integrations. All commands are run from the `backend/` directory.

### Run All Tests

```bash
python manage.py test accounts.tests skillhub.tests
```

### Run Tests with Verbose Output

```bash
python manage.py test accounts.tests skillhub.tests --verbosity=2
```

### Run Tests for a Specific App

```bash
python manage.py test accounts.tests   # Only accounts tests
python manage.py test skillhub.tests   # Only skillhub tests
```

### Run a Specific Test File, Class, or Method

```bash
# Run a specific file
python manage.py test accounts.tests.test_models

# Run a specific test class
python manage.py test accounts.tests.test_models.UserModelTestCase

# Run a single test method
python manage.py test accounts.tests.test_models.UserModelTestCase.test_create_user_with_valid_data
```

### Check Test Coverage

"Coverage" tells you what percentage of the code is tested.

```bash
# Step 1 — Run tests and collect coverage data
coverage run --source='accounts,skillhub' manage.py test accounts.tests skillhub.tests

# Step 2 — View results in the terminal
coverage report

# Step 3 — Generate a detailed HTML report (open htmlcov/index.html in your browser)
coverage html
```

**Expected coverage results:**

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

> The project maintains approximately **95% test coverage** — meaning nearly every line of code is tested.

### Using the Convenience Script

A shortcut script is available at `backend/run_tests.sh`:

```bash
cd backend
chmod +x run_tests.sh   # Make it executable (one time only)

./run_tests.sh           # Run all tests with coverage
./run_tests.sh -v        # Verbose output
./run_tests.sh -p        # Run in parallel (faster)
./run_tests.sh -f        # Stop immediately on first failure
./run_tests.sh -n        # Run without coverage measurement
./run_tests.sh -r        # Show existing coverage report only
```

---

## 15. Security & Performance

### 🔒 Security Features

| Feature | Description |
|---|---|
| **JWT Authentication** | Industry-standard token-based login. Tokens expire, limiting risk if stolen. |
| **Rate Limiting** | Prevents brute force attacks (login) and API abuse (skills, feedback). |
| **File Upload Validation** | Profile picture uploads are validated using Pillow to ensure only images are accepted. |
| **Role-Based Permissions** | Admins and regular users have different levels of access. |
| **Object-Level Permissions** | Users can only modify their own data (profiles, skills, feedback). |
| **Secure Password Hashing** | Passwords are never stored in plain text — Django uses PBKDF2 hashing by default. |
| **CORS Configuration** | Cross-origin requests are controlled (allow all in dev, restrict in production). |

### ⚡ Performance Features

| Feature | Description |
|---|---|
| **Optimized DB Queries** | Uses `select_related` and `prefetch_related` to minimize database queries. |
| **Pagination** | List views return 10–20 results per page, preventing large data loads. |
| **Database Indexing** | Frequently queried fields (name, category, status) have database indexes for fast lookups. |
| **Efficient File Handling** | Profile pictures are processed with Pillow and stored with date-based folder paths. |

---

## 16. Roadmap

### Frontend (Currently ~40% Complete)

**✅ Already working:**
- Authentication context and token management
- User profile display
- Exchange list display
- Basic registration and login UI

**🚧 Still to be built (~60% remaining):**
- Complete registration/login flows with full error handling
- Skill exchange request creation UI
- Milestone tracking interface
- Feedback submission and viewing UI
- Search, filters, and location-based discovery
- Fully responsive design across all pages

### Future Enhancements

| Feature | Description |
|---|---|
| 🤖 AI Matching | Smart skill recommendations based on user interests and history |
| 🏆 Gamification | Badges, points, and achievement systems to encourage engagement |
| 👥 Group Learning | Community events and group-based skill exchanges |
| 💳 Premium Tiers | Optional paid mentorship for specialized or high-demand skills |
| 📹 Video Integration | Built-in video call feature for conducting learning sessions |
| 🏅 Leaderboards | Weekly rankings of top teachers and learners |

---

## 17. Contributing

Contributions are welcome! Here's how to get involved:

### Bug Reports & Feature Requests

1. Check [existing issues](https://github.com/himanshu-suthar-simform/skillswap/issues) to see if it's already reported.
2. Open a new issue with a clear title and detailed description.

### Contributing Code

1. **Fork** the repository on GitHub
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and write tests if applicable
4. **Run the tests** to make sure nothing is broken:
   ```bash
   cd backend && python manage.py test accounts.tests skillhub.tests
   ```
5. **Commit your changes** using conventional commit format:
   ```bash
   git commit -m "feat: add skill recommendation feature"
   git commit -m "fix: correct exchange status transition bug"
   git commit -m "docs: update API documentation for feedback"
   ```
6. **Push to your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** on GitHub describing what you changed and why

### Commit Message Prefixes

| Prefix | When to use |
|---|---|
| `feat:` | Adding a new feature |
| `fix:` | Fixing a bug |
| `docs:` | Documentation changes |
| `style:` | Code formatting (no logic changes) |
| `refactor:` | Code restructuring (no feature/bug changes) |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance tasks (dependency updates, config changes) |

### Code Style

The backend uses **Black** (Python formatter) and **isort** (import sorter), configured via pre-commit hooks:

```bash
cd backend
pip install pre-commit
pre-commit install
```

This will automatically format your code when you commit.

---

## 18. License

SkillSwap is open-source software licensed under the **MIT License**.

This means you are free to:
- ✅ Use it for personal or commercial projects
- ✅ Modify the code
- ✅ Distribute your version

The only requirement is to include the original license notice.

See the full license text in the [LICENSE](LICENSE) file.

---

<div align="center">

**Built with ❤️ to make learning free and accessible for everyone.**

[⭐ Star on GitHub](https://github.com/himanshu-suthar-simform/skillswap) • [🐛 Report a Bug](https://github.com/himanshu-suthar-simform/skillswap/issues) • [💡 Request a Feature](https://github.com/himanshu-suthar-simform/skillswap/issues)

</div>
