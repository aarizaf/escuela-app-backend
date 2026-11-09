import os

# Valores por defecto para pruebas locales (Postgres de docker-compose). Nunca apuntan a Supabase.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/escuela"
)
os.environ.setdefault(
    "DATABASE_DIRECT_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/escuela"
)
os.environ.setdefault("DATABASE_SSL", "disable")
os.environ.setdefault("JWT_SECRET", "test-secret-test-secret-test-secret-123")
