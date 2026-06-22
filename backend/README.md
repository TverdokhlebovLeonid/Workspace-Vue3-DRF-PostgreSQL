# Backend — Workspace API

Django REST API with JWT authentication, `ADMIN` / `USER` roles, and PostgreSQL.

See the [root README](../README.md) for setup and Docker commands.

## Layout

```
backend/
├── manage.py
├── fixtures/demo/
├── config/          # settings, urls, env helpers
└── apps/
    ├── users/
    ├── schedules/
    ├── documents/
    └── common/
```

## Local run

```powershell
uv sync
copy .env.example .env
docker compose -f ../docker-compose.backend.yml up db -d
uv run python manage.py migrate
uv run python manage.py bootstrap_admin
uv run python manage.py runserver
```

API: http://127.0.0.1:8000/api/  
Swagger (dev): http://127.0.0.1:8000/api/schema/swagger-ui/

## Commands

```powershell
uv run python manage.py migrate
uv run python manage.py bootstrap_admin
uv run python manage.py seed_work_rules
uv run python manage.py load_demo_data
uv run python manage.py load_demo_data --clear
uv run python manage.py clear_app_data
uv sync --group dev
uv run ruff format apps config
uv run ruff check apps config --fix
```
