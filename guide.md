# SkillSwap — Functional Requirements Document (FRD)

## 1. Project Overview

**Project Name:** SkillSwap
**Purpose:**
SkillSwap is a peer-to-peer skill exchange platform where users can teach and learn skills directly from one another.
It encourages mutual learning — for example, one user can teach Python while learning JavaScript from another.

The app aims to build a community of continuous learners and teachers through skill-sharing, feedback, and collaboration.

---

## 2. Objectives

- Enable users to list their skills and find matching learners or teachers.
- Facilitate a barter-style exchange: “I teach you X, you teach me Y.”
- Encourage community growth through progress tracking, feedback, and leaderboards.
- Provide an easy-to-use chat and progress interface for communication and learning updates.

---

## 3. Scope

### In-Scope (for current demo)
- User registration and authentication
- Role-based access (Admin, Learner/Teacher)
- Skill listing with details (description, duration, milestones)
- Skill exchange requests between users
- Simple progress tracking (mark as done)
- Feedback and rating after completion
- Leaderboard (Top 10 teachers and learners of the week)
- One-to-one chat feature between users

### Out of Scope (for demo version)
- Payment or monetization
- Complex progress tracking (time logs, detailed milestones)
- Advanced matching or recommendation algorithms
- AI-based chat or skill suggestions

---

## 4. User Roles

### 1. **Admin**
- Manage users (approve/block)
- Monitor overall platform activity
- Moderate feedback and reports
- Manage leaderboard resets (weekly)

### 2. **Learner/Teacher (General User)**
- Register and maintain personal profile
- Add skills they can teach
- Add skills they want to learn
- Request to learn a skill from another user
- Accept or reject skill exchange requests
- Track learning progress (mark as done)
- Provide and view feedback
- Chat with the other user during exchange

---

## 5. Functional Requirements

### 5.1 User Management
- Users can register using email and password.
- Users can update profile information (bio, profile picture, etc.).
- Admin can view, approve, or deactivate users.
- Each user must have a role assigned (Admin / Learner-Teacher).

### 5.2 Skill Management
- A user can add multiple skills they can teach.
- Each skill includes:
  - Skill name
  - Description
  - Estimated duration (days/hours)
  - Milestones (optional)
- Other users can view listed skills of others.

### 5.3 Skill Exchange System
- A user can send a “Skill Request” to learn a skill.
- The request includes:
  - Skill to learn
  - Skill offered in return
- The other user can accept or reject the request.
- Once accepted, both users are paired for learning.

### 5.4 Progress Tracking
- Once a learning session starts, each user can mark progress as *Done*.
- Completion status updates both users’ profiles and contributes to leaderboard scoring.

### 5.5 Feedback System
- After completion, both users provide ratings and feedback for each other.
- Feedback will be visible on each user’s profile.
- Admin can review and moderate feedback if needed.

### 5.6 Leaderboard
- Leaderboard shows **Top 10 Teachers** and **Top 10 Learners** of the week.
- Ranking is based on:
  - Number of completed exchanges
  - Average feedback rating
- Admin can reset leaderboard weekly.

### 5.7 Chat System
- One-to-one chat between paired users during an ongoing exchange.
- Chat limited to text messages (for demo).
- Chat access ends when the exchange is completed.

---

## 6. Non-Functional Requirements

### 6.1 Usability
- Intuitive and simple UI for all age groups.
- Consistent navigation and clear feedback messages.

### 6.2 Performance
- API response time < 2 seconds for basic actions.
- Leaderboard updates automatically (or via scheduled job weekly).

### 6.3 Security
- Authentication via JWT tokens.
- Role-based permission control.
- Secure password storage and encrypted data transmission.

### 6.4 Scalability
- Should support future integration with payment gateways or AI-based recommendations.
- Modular architecture to allow easy feature expansion.

---

## 7. Future Enhancements (Post-Demo)

- AI-based skill matching and recommendations.
- Gamification (badges, points, achievements).
- Group-based learning or community events.
- Payment integration for premium mentorship.
- Video call or meeting integration.

---

## 8. Success Metrics

- Number of successful skill exchanges.
- Active user count per week.
- Average feedback rating per user.
- Leaderboard participation and engagement metrics.

---

## 9. Assumptions and Constraints

- Internet connection is required for all operations.
- Each user can act as both learner and teacher simultaneously.
- System will initially support English only.
- Limited to one-on-one exchanges (no group learning yet).

---

## 10. Deliverables

- Functional Django REST Framework backend.
- Optional React-based frontend for demonstration.
- Postman collection or Swagger API documentation.
- Database schema diagram.
- Sample data for testing.

---

## 11. Timeline (for Demo)

| Phase | Task | Duration |
|-------|------|-----------|
| Day 1 | Setup backend, user model, authentication, roles | 0.5 day |
| Day 1 | Skill model and listing endpoints | 0.5 day |
| Day 2 | Skill exchange logic, progress, feedback | 1 day |
| Day 3 | Leaderboard, chat, testing & documentation | 1 day |

---

## 12. Tech Stack (Tentative)

| Layer | Technology |
|-------|-------------|
| Backend | Django REST Framework |
| Database | PostgreSQL / SQLite (for demo) |
| Authentication | JWT (Simple JWT) |
| Frontend | React.js (optional lightweight UI) |
| Chat | Django Channels / WebSocket (basic demo) |
| Deployment | Docker (optional for packaging) |

---

## 13. Conclusion

SkillSwap promotes a learning ecosystem where users become both mentors and students.
The platform’s simplicity and flexibility make it ideal for future scalability — whether for personal learning, community education, or global knowledge exchange.
