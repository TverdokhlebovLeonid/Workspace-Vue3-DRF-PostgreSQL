# Demo data

Files in this folder are for **local development and testing only**. Do not use demo passwords in production.

## Contents

| File | Description |
|------|-------------|
| `dataset.json` | Admin, locations, employees with passwords, schedule generation flag |

## Commands

```powershell
uv run python manage.py migrate
uv run python manage.py seed_work_rules
uv run python manage.py bootstrap_admin

uv run python manage.py load_demo_data
uv run python manage.py clear_app_data
uv run python manage.py load_demo_data --clear
```

## Editing

1. Change `dataset.json`.
2. Run `load_demo_data --clear`.

Keys `key`, `location_keys`, and `work_rule_codes` link records inside the file. UUIDs are generated on load.
