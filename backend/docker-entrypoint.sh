#!/bin/sh
set -e

python <<'EOF'
import os
import socket
import sys
import time

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))

for attempt in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    sys.exit("PostgreSQL is not available")

print(f"PostgreSQL is ready at {host}:{port}")
EOF

python manage.py migrate --noinput

exec "$@"
