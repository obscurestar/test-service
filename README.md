# User Service

FastAPI service backed by PostgreSQL and SQLAlchemy. Start the API, primary database, and streaming replica with:

```sh
docker compose up --build
```

The API listens on `http://localhost:6000`. The primary and replica databases are available to the API on the Compose network and are not published to the host. The replica follows the primary using PostgreSQL physical WAL streaming.

## Endpoints

- `GET /healthcheck` returns `OK`.
- `GET /newuser?first_name=Jane&last_name=Doe` creates or finds a user.
- `POST /newuser` accepts JSON such as `{"first_name":"Jane","last_name":"Doe"}`.
- `GET /hello?user_id=<uuid>` greets a known user and records a visit.
- `POST /hello` accepts JSON such as `{"user_id":"<uuid>"}`.
- `POST /spy` accepts JSON such as `{"user_id":"<uuid>"}` and returns the matching user row from the replica, or `Invalid User ID` if it does not exist.

Example POST:  curl -X POST http://localhost:6000/hello -H "Content-Type: application/json" -d '{"user_id":"14ed842c-9aa9-4809-910c-3fb3e2e85926"}'

Names are limited to 32 characters. A repeated name lookup updates `last_access` and increments `use_count`; a newly created user starts with a count of zero. `last_access` stores the current date, as defined by the database schema. The primary records DDL command completions and dropped objects in the `ddl_audit` table; these audit rows are included in WAL replication.

Set `POSTGRES_PASSWORD` in `.env` for the primary database. `REPLICATION_PASSWORD` can be set separately; if omitted, it uses `POSTGRES_PASSWORD`. Set `DATABASE_URL` and `REPLICA_DATABASE_URL` to override the connection strings outside Compose.
