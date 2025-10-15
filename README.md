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

8. Run the development server:
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
