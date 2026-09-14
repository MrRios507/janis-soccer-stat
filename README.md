# janis-soccer-stat

See `docs/vision.md` for what this project is and why.

## Local setup

```bash
cp .env.example .env      # then edit .env with your own local credentials
uv sync                   # install dependencies into .venv
docker compose up -d      # start Postgres 16 locally
```

Requires Python 3.11+ and Docker.
