# Base44 Dev Environment

## What this repo is
GitHubDaily is a **content-only** repository — curated lists of open-source projects organized by year (2018–2024) in Markdown files. There is no original application code; `server.py` and `requirements.txt` were added by Base44 to render the Markdown as a browsable web site.

## How it runs
- `docker-compose.base44.yml` uses `python:3.12-slim`, bind-mounts the repo at `/app`, installs Flask + Markdown on startup, and runs `server.py` (Flask dev server with auto-reload on port 3000).
- No external credentials or secrets are needed.
- No database or other infrastructure services.

## Routes
- `/` — README.md (main curated list)
- `/2024`, `/2023`, … `/2018` — year-specific summaries
- `/articles` — list of article Markdown files
- `/articles/<idx>` — individual article

## Verifying it works
- `docker compose -f docker-compose.base44.yml up -d --build`
- `curl -s http://localhost:3000/` should return rendered HTML with the GitHubDaily content.
- Container healthcheck probes `GET /` via Python urllib.
