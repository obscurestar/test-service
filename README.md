# User Service

FastAPI service backed by PostgreSQL and SQLAlchemy. Start the API and database with:

```sh
docker compose up --build
```

The API listens on `http://localhost:6000`. The database is available to the API on the Compose network and is not published to the host.

## Endpoints

- `GET /healthcheck` returns `OK`.
- `GET /newuser?first_name=Jane&last_name=Doe` creates or finds a user.
- `POST /newuser` accepts JSON such as `{"first_name":"Jane","last_name":"Doe"}`.
- `GET /hello?user_id=<uuid>` greets a known user and records a visit.
- `POST /hello` accepts JSON such as `{"user_id":"<uuid>"}`.

Example POST:  curl -X POST http://localhost:6000/hello -H "Content-Type: application/json" -d '{"user_id":"14ed842c-9aa9-4809-910c-3fb3e2e85926"}'

Names are limited to 32 characters. A repeated name lookup updates `last_access` and increments `use_count`; a newly created user starts with a count of zero. `last_access` stores the current date, as defined by the database schema.

The development database credentials are configured in `compose.yaml`. Set `DATABASE_URL` to override the connection string outside Compose.
