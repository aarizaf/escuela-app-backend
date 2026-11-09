# escuela-api

Backend (FastAPI + PostgreSQL) de escuela-app. Supabase se usa **solo como infraestructura**
(PostgreSQL y Storage); la autenticación es propia y la app móvil nunca habla con Supabase.

## Desarrollo local

Requisitos: Python 3.12+, Docker.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env                                 # completar valores
docker compose up -d db                              # PostgreSQL local
alembic upgrade head
uvicorn app.main:app --reload                        # http://localhost:8000/docs
```

Pruebas y calidad: `pytest`, `ruff check .`, `ruff format --check .`, `mypy app`.
Las pruebas usan el PostgreSQL de Docker, **nunca** Supabase.

## Fase 0 — Preparar Supabase (pasos manuales)

> Los puertos y nombres de host cambian con el tiempo: confírmalos en
> *Project → Connect* del panel y en la documentación de Supabase.

1. **Crear el proyecto** en la región más cercana a los usuarios (para Colombia suele ser
   `sa-east-1`, São Paulo). Anota la región: AWS usará la misma. Guarda la contraseña de la
   base de datos en un gestor de secretos.
2. **Cadenas de conexión** (*Connect* en el panel). Necesitas tres:
   | Uso | Tipo | Puerto típico | Variable |
   |---|---|---|---|
   | API (uso normal) | Pooler, modo **transaction** | 6543 | `DATABASE_URL` (con `DATABASE_POOLER_TRANSACTION_MODE=true`) |
   | Alembic | Pooler modo **session** o conexión directa | 5432 | `DATABASE_DIRECT_URL` |
   El usuario del pooler tiene la forma `usuario.<project-ref>`. La conexión directa suele ser
   solo IPv6 salvo que contrates el add-on IPv4; si tu red no soporta IPv6 usa el pooler en
   modo session. Cambia el esquema a `postgresql+asyncpg://` y usa `DATABASE_SSL=require`.
3. **Rol de la aplicación** (SQL Editor, una sola vez; es la única excepción a "no tocar desde
   el panel", porque los roles no viven en migraciones):
   ```sql
   CREATE ROLE escuela_app LOGIN PASSWORD '<clave-larga-aleatoria>';
   GRANT CONNECT ON DATABASE postgres TO escuela_app;
   GRANT USAGE ON SCHEMA public TO escuela_app;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public
     GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO escuela_app;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO escuela_app;
   ```
   `DATABASE_URL` usa `escuela_app`; `DATABASE_DIRECT_URL` usa `postgres` (dueño de las tablas)
   mientras se corren migraciones. Las migraciones de la fase 2 también harán `REVOKE` a
   `anon`/`authenticated` y activarán RLS en cada tabla.
   > Con RLS activo y sin políticas, `escuela_app` no vería filas salvo que tenga `BYPASSRLS`
   > o sea dueño de las tablas. Lo resolvemos en la fase 2 (se decide entre dar `BYPASSRLS`
   > al rol o crear una política explícita para él; ambos son PostgreSQL estándar).
4. **Buckets privados** (*Storage*): crea `avatars`, `submissions` y `posts` con "Public bucket"
   **desactivado**.
5. **Credenciales S3 de Storage** (*Storage → S3 Connection*): crea un access key y anota
   endpoint, región, `S3_ACCESS_KEY_ID` y `S3_SECRET_ACCESS_KEY`. (Se usan desde la fase 3.)
6. **Desactivar la API de datos** (*Project Settings → Data API*), si el plan lo permite. No
   usamos PostgREST ni la clave `anon`.
7. **Secretos**: `.env` solo en el servidor/local, nunca en git. La `service_role key` no se
   necesita con el backend S3; no la copies al proyecto.

## Estructura

```
app/          main.py, core/ (config, seguridad), db/, models/, schemas/, routers/, services/,
              integrations/ (storage, mailer)
migrations/   Alembic (fuente de verdad del esquema)
tests/        unit/ e integration/
docs/contract Contrato de la app (types, api.ts, schema.sql)
```
