# LifeFlow Backend

Gamified productivity scheduler API built with Django + Django REST Framework.

## Tech Stack

- Django 5.1 + Django REST Framework
- PostgreSQL
- JWT Authentication (SimpleJWT)
- Celery + Redis (task scheduling)
- Docker + Docker Compose
- drf-spectacular (OpenAPI docs)

## Quick Start

### With Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

### Without Docker

```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements/dev.txt

# Copy env file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/login/` | POST | Get JWT tokens |
| `/api/auth/token/refresh/` | POST | Refresh access token |
| `/api/auth/profile/` | GET/PUT | User profile |
| `/api/tasks/` | GET/POST | List/create tasks |
| `/api/tasks/{id}/` | GET/PUT/DELETE | Task detail |
| `/api/tasks/today/` | GET | Today's tasks |
| `/api/tasks/{id}/complete/` | POST | Complete a task |
| `/api/tasks/missed/` | GET | Missed tasks |
| `/api/gamification/achievements/` | GET | All achievements |
| `/api/gamification/achievements/mine/` | GET | User's achievements |
| `/api/gamification/xp-logs/` | GET | XP history |
| `/api/gamification/streaks/` | GET | Streak records |
| `/api/gamification/challenges/` | GET | Today's challenges |
| `/api/scheduler/rules/` | GET/POST | Recurring rules |
| `/api/docs/` | GET | Swagger UI |

## Project Structure

```
lifeflow-backend/
├── apps/
│   ├── authentication/   # Custom user, JWT auth
│   ├── tasks/            # Task CRUD, completion logic
│   ├── scheduler/        # Recurring tasks, rollover, Celery tasks
│   ├── gamification/     # XP, achievements, streaks, challenges
│   ├── analytics/        # (Phase 4)
│   ├── notifications/    # (Phase 4)
│   └── common/           # Base models
├── config/
│   ├── settings/         # base, dev, prod
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── docker-compose.yml
├── Dockerfile
└── requirements/
```

## Scheduler Logic

- **Recurring tasks**: Auto-generated daily via Celery. If missed, they disappear (penalty applied). Fresh instance next day.
- **Non-recurring tasks**: If missed, rolled over to next day with penalty. Rollover count tracked.
- **Streaks**: Updated daily. Perfect days boost discipline score.
- **Chaos meter**: Increases with missed tasks, decreases with completions.

## Development Phases

- [x] Phase 1: Auth, Tasks CRUD, Gamification models, Scheduler
- [ ] Phase 2: Full scheduler engine, dashboard API
- [ ] Phase 3: Achievements, daily challenges, XP engine
- [ ] Phase 4: Analytics, notifications, calendar
- [ ] Phase 5: AI features, mobile optimization
