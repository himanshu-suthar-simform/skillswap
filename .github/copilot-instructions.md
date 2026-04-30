# SkillSwap — GitHub Copilot Repository Instructions

## Project Overview

SkillSwap is a peer-to-peer skill-exchange platform where users teach what they know and learn what they want — no money, just skill-for-skill exchanges.

- **Backend:** Django 5 + Django REST Framework 3, JWT auth (SimpleJWT), Celery + Redis for background tasks, drf-spectacular for API docs
- **Frontend:** React 19, React Router v7, TanStack Query v5, Tailwind CSS, react-hook-form + Yup, Axios, react-toastify

---

## General Coding Standards

- Write clean, self-documenting code. Add comments only when the logic is non-obvious.
- Prefer explicit over implicit — avoid magic values; use named constants or enums.
- Keep functions and components small and focused on a single responsibility.
- Never commit secrets, API keys, or credentials. Use environment variables and `.env` files.
- Always handle errors explicitly; do not silently swallow exceptions.
- Follow the existing code style and naming conventions found in each layer of the project.

---

## Backend (Django / DRF)

### Project Layout

```
backend/
├── accounts/     # User auth, profiles, JWT
├── general/      # Shared utilities, pagination, permissions
├── skillhub/     # Skill exchange, milestones, feedback
└── skillswap/    # Django project config & Celery
```

### Django Guidelines

- Follow Django's MVT pattern. Keep business logic in models or dedicated service modules, not in views.
- Use class-based views (`APIView`, `GenericAPIView`, `ViewSet`) from DRF rather than function-based views unless there is a strong reason.
- Always use DRF serializers for input validation and output serialization — never access `request.data` directly in views without a serializer.
- Apply permissions (`IsAuthenticated`, custom permission classes) on every view. Default to deny-all, then explicitly allow.
- Use `select_related` / `prefetch_related` to avoid N+1 queries.
- Register all URLs through the DRF router or `urls.py` — no ad-hoc URL registration.
- Use `get_object_or_404` instead of bare `Model.objects.get(...)` in views.

### API Design

- Follow RESTful conventions: nouns for resources, HTTP verbs for actions.
- Version APIs under `/api/v<n>/` if breaking changes are introduced.
- Return consistent error responses using DRF's standard exception handling.
- Document every endpoint with drf-spectacular decorators (`@extend_schema`).

### Authentication

- All protected endpoints require a valid JWT Bearer token.
- Use `SimpleJWT` refresh/access token flow. Do not store tokens in cookies unless explicitly required.

### Celery / Background Tasks

- Place task definitions in `<app>/tasks/` modules.
- Tasks must be idempotent where possible.
- Always set a timeout (`time_limit`) on tasks that may run long.
- Use `django-celery-beat` for periodic tasks; prefer the management command (`create_periodic_task`) over hard-coded schedules in `celery.py`.

### Testing

- Write tests with Django's `TestCase` and DRF's `APITestCase`.
- Run tests from `backend/`: `python manage.py test accounts.tests skillhub.tests`
- Use `coverage` to measure coverage: target ≥ 90 % per app.
- Test happy paths, validation errors, permission denials, and edge cases.

---

## Frontend (React)

### Project Layout

```
frontend/src/
├── api/          # Axios API client and per-resource request helpers
├── components/   # Reusable UI components
├── context/      # React context providers (e.g. AuthProvider)
├── hooks/        # Custom React hooks
├── pages/        # Page-level components mapped to routes
└── routes/       # React Router route configuration
```

### React Guidelines

- Use **functional components** with hooks exclusively — no class components.
- Extract reusable logic into custom hooks in `src/hooks/`.
- Keep page-level components in `src/pages/` and shared UI in `src/components/`.
- Use **TanStack Query** (`useQuery`, `useMutation`) for all server-state fetching and caching; do not manage server state with `useState`/`useEffect`.
- Use **react-hook-form** with **Yup** schemas for all forms and input validation.
- Display async feedback (loading, success, error) using **react-toastify**.
- Use **Tailwind CSS** utility classes for styling. Do not write inline styles or separate CSS files unless absolutely necessary.
- Prefer `clsx` for conditional class name composition.

### API Layer

- All HTTP calls go through `src/api/api.js` (the Axios instance). Add resource-specific helpers in the relevant `src/api/<resource>.js` file.
- Never call `axios` directly from components or hooks — always go through the API helpers.
- Read the base URL from `process.env.REACT_APP_API_URL`.

### Routing

- Define and manage all routes in `src/routes/AppRouter.jsx`.
- Use React Router v7 `<Link>` and `useNavigate` — do not manipulate `window.location` directly.
- Protect authenticated routes with the auth context from `AuthProvider`.

### Environment Variables

- Prefix all frontend env vars with `REACT_APP_`.
- Provide defaults in `frontend/.env.example`; never commit real `.env` files.

### Testing

- Use React Testing Library (`@testing-library/react`) for component tests.
- Run tests from `frontend/`: `npm test`

---

## Git & Collaboration

- Branch naming: `feature/<short-description>`, `fix/<short-description>`, `chore/<short-description>`
- Commit messages: follow Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`).
- Open an issue before submitting a pull request for non-trivial changes.
- Pull requests must pass all CI checks before merging.
