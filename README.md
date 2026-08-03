# Incident Tracker

A backend system for tracking server health and incidents, inspired by 
enterprise ITSM tools (ServiceNow) I used daily in a cloud operations role.

## Live links
- **API Docs:** https://incident-tracker-93cm.onrender.com/docs
- **Dashboard (requires API key):** https://incident-tracker-93cm.onrender.com/dashboard

*Note: hosted on Render's free tier, so the first request after inactivity may take 30-60 seconds to wake up.*

## Why I built this
At Infosys, I manually monitored AWS infrastructure and logged incidents 
in ServiceNow. This project automates that same workflow: it monitors 
servers, auto-creates incidents when health checks fail, and tracks them 
through resolution — the system I used to operate, now built by me.

## Features
- REST API (FastAPI) for managing servers, incidents, and incident logs
- PostgreSQL database (hosted on Neon) with relational schema
- Automated background health checks (APScheduler) that auto-create 
  incidents on failure — no manual monitoring required
- API key authentication
- Simple dashboard for viewing live server/incident status
- Containerized with Docker for consistent, portable deployment

## Tech stack
Python, FastAPI, SQLAlchemy, PostgreSQL, APScheduler, Docker

## Running locally
1. Clone the repo, create a virtual environment, `pip install -r requirements.txt`
2. Create a `.env` file with `DATABASE_URL` and `API_KEY`
3. `python create_tables.py`
4. `uvicorn app.main:app --reload`
5. Visit `/docs` for the API, `/dashboard` for the UI

## Running with Docker
1. `docker build -t incident-tracker .`
2. `docker run -p 8000:8000 --env-file .env incident-tracker`

## Related project
Infrastructure provisioning for this kind of system, practiced separately in Terraform: 
[terraform-s3-demo](https://github.com/mafzaldbd/terraform-s3-demo)

## CI/CD
Every push to `main` automatically triggers a GitHub Actions workflow that builds 
the Docker image, catching broken builds before deployment. See 
`.github/workflows/docker-build.yml`.

## What I'd add next
- Real health checks (HTTP ping / server agent) instead of simulated data
- Kubernetes deployment for the API layer
- Extend CI pipeline to run automated tests before the build step