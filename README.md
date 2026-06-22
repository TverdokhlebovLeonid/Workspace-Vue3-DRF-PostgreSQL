# Workspace

Full-stack application: **Vue 3 + Django REST Framework + PostgreSQL**.

- JWT authentication, roles `ADMIN` / `USER`
- Swagger (dev/staging only): `/api/schema/swagger-ui/`
- Brand color: `#000083`

## Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | Vue 3, TypeScript, Pinia, Tailwind CSS 4, Axios, Vite |
| Backend | Django 6, DRF, SimpleJWT, drf-spectacular, uv |
| Database | PostgreSQL 17 |

## Structure

```
Workspace/
├── backend/                 # Django API
│   ├── Dockerfile
│   └── fixtures/demo/       # optional demo data (dataset.json)
├── frontend/                # Vue SPA
│   └── Dockerfile
├── docker-compose.yml       # db + backend + frontend
└── docker-compose.backend.yml  # db + backend only
```

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose v2)

For local development without Docker:

- Node.js 20+
- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL 17

---

## First run: create an administrator

After `migrate`, there are **no application users**. Create the first admin **manually once**.

### 1. Configure `.env`

```powershell
copy backend\.env.example backend\.env
```

Add to `backend/.env`:

```env
BOOTSTRAP_ADMIN_USERNAME=admin
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD=YourStrongPassword123
```

> `POSTGRES_USER` / `POSTGRES_PASSWORD` are **database** credentials, not application login.

### 2. Start backend + PostgreSQL

```powershell
docker compose -f docker-compose.backend.yml up --build -d
```

### 3. Create the first admin

```powershell
docker compose -f docker-compose.backend.yml exec backend python manage.py bootstrap_admin
```

### 4. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and sign in with `BOOTSTRAP_ADMIN_USERNAME` / `BOOTSTRAP_ADMIN_PASSWORD`.

---

## Quick start: full stack in Docker

```powershell
copy backend\.env.example backend\.env
docker compose up --build -d
docker compose exec backend python manage.py bootstrap_admin
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8080 |
| Backend API | http://localhost:8000/api/ |
| Swagger | http://localhost:8000/api/schema/swagger-ui/ |
| PostgreSQL | localhost:5432 |

Stop: `docker compose down`  
Remove DB volume: `docker compose down -v`

On startup the backend waits for PostgreSQL and runs migrations. **It does not create users.**

All entities use **UUID primary keys**. After schema changes, recreate the database: `docker compose down -v` → `up --build`.

---

## Database: empty or demo

Demo data lives in [`backend/fixtures/demo/`](backend/fixtures/demo/) (`dataset.json`).

### Option A — empty database

Schema, work rules seed, and **one admin** from `.env`:

```powershell
docker compose -f docker-compose.backend.yml exec backend python manage.py migrate
docker compose -f docker-compose.backend.yml exec backend python manage.py seed_work_rules
docker compose -f docker-compose.backend.yml exec backend python manage.py bootstrap_admin
```

Local without Docker:

```powershell
cd backend
uv run python manage.py migrate
uv run python manage.py seed_work_rules
uv run python manage.py bootstrap_admin
```

### Option B — demo dataset

Locations, four employees with accounts, admin, and a **generated schedule**:

```powershell
docker compose -f docker-compose.backend.yml exec backend python manage.py migrate
docker compose -f docker-compose.backend.yml exec backend python manage.py load_demo_data
```

Reload demo from scratch:

```powershell
docker compose -f docker-compose.backend.yml exec backend python manage.py load_demo_data --clear
```

Clear app data only (keeps migrations):

```powershell
docker compose -f docker-compose.backend.yml exec backend python manage.py clear_app_data
```

### Demo accounts (`load_demo_data`)

| Role | Login | Password |
|------|-------|----------|
| Admin | `admin` | see `dataset.json` |
| User | `ivan`, `maria`, `alex`, `olga` | see `dataset.json` |

> Demo passwords are for **local development only**. In production use `bootstrap_admin` and your own users.

---

## Backend + PostgreSQL only

```powershell
copy backend\.env.example backend\.env
docker compose -f docker-compose.backend.yml up --build -d
docker compose -f docker-compose.backend.yml exec backend python manage.py bootstrap_admin
```

Frontend locally:

```powershell
cd frontend
npm install
npm run dev
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/jwt/create/` | Login (JWT) |
| POST | `/api/auth/jwt/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Current user |
| GET/POST | `/api/auth/users/` | List / create users (ADMIN) |
| DELETE | `/api/auth/users/{uuid}/` | Delete user (ADMIN) |
| GET | `/api/auth/health/` | Health check (+ DB) |

---

## Environment variables (backend)

| Variable | Dev | Description |
|----------|-----|-------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | Settings module |
| `SECRET_KEY` | dev fallback | Django secret (**required** in prod) |
| `DEBUG` | `True` | Debug mode |
| `POSTGRES_*` | see `.env.example` | PostgreSQL connection |
| `CORS_ALLOWED_ORIGINS` | localhost:5173,8080 | Frontend origins |
| `ENABLE_API_DOCS` | `True` | Swagger on/off |
| `BOOTSTRAP_ADMIN_*` | — | For `bootstrap_admin` only |

Production: `DJANGO_SETTINGS_MODULE=config.settings.prod`, all secrets required, `DEBUG=False`, `ENABLE_API_DOCS=False`.

---

## Local development without Docker

### PostgreSQL

```powershell
docker compose -f docker-compose.backend.yml up db -d
```

### Backend

```powershell
cd backend
uv sync
copy .env.example .env
uv run python manage.py migrate
uv run python manage.py bootstrap_admin
uv run python manage.py runserver
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

---

## Useful commands

```powershell
docker compose logs -f
docker compose exec backend python manage.py bootstrap_admin
docker compose exec backend python manage.py seed_work_rules
docker compose exec backend python manage.py load_demo_data
docker compose exec backend python manage.py load_demo_data --clear
docker compose exec backend python manage.py clear_app_data

cd frontend && npm run lint && npm run format
cd backend && uv sync --group dev && uv run ruff format apps config
```

---

## Build Docker images separately

```powershell
docker build -t workspace-backend ./backend
docker build -t workspace-frontend ./frontend
```
