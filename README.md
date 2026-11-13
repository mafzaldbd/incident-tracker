# Incident Tracker

A backend system for tracking server health and incidents, inspired by
enterprise ITSM tools (ServiceNow) I used daily in a cloud operations role.

## Live links

- **API Docs:** <https://incident-tracker-93cm.onrender.com/docs>
- **Dashboard (requires API key):** <https://incident-tracker-93cm.onrender.com/dashboard>

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
- CI/CD pipeline that builds the image and pushes it to Amazon ECR using GitHub OIDC (no stored AWS keys)
- Also deployed on AWS (EC2 with a private RDS database and Secrets Manager) using Terraform

## Tech stack

Python, FastAPI, SQLAlchemy, PostgreSQL, APScheduler, Docker, GitHub Actions, Amazon ECR, Terraform, AWS (EC2, RDS, Secrets Manager)

## Running locally

1. Clone the repo, create a virtual environment, `pip install -r requirements.txt`
2. Create a `.env` file with `DATABASE_URL` and `API_KEY`
3. `python create_tables.py`
4. `uvicorn app.main:app --reload`
5. Visit `/docs` for the API, `/dashboard` for the UI

## Running with Docker

1. `docker build -t incident-tracker .`
2. `docker run -p 8000:8000 --env-file .env incident-tracker`

## CI/CD

The workflow in `.github/workflows/ecr.yml` runs on GitHub Actions:

- **On every pull request:** builds the Docker image, catching broken builds before merge.
- **On merge to `main`:** authenticates to AWS with GitHub OIDC, using a short-lived IAM role limited to a single ECR repository (no AWS keys stored in GitHub), then pushes the image tagged with the commit SHA and `latest`.

### Pull request: image build check

![Pull request build check](docs/ecr-pr-build.png)

### Merge to main: authenticate and push to ECR

The run is shown in two screenshots, because the steps didn't fit in one.

![GitHub Actions push to ECR, part 1](docs/ecr-push-actions.png)

![GitHub Actions push to ECR, part 2](docs/ecr-push-actions-1.png)

### Result: image in Amazon ECR

![Image in Amazon ECR](docs/ecr-image.png)

## Deployment on AWS

The same image runs on an EC2 instance, connected to a private RDS PostgreSQL database, with credentials read from AWS Secrets Manager. The infrastructure is provisioned with reusable Terraform modules, dev and prod environments, and S3 remote state: [terraform-aws-vpc-ec2](https://github.com/mafzaldbd/terraform-aws-vpc-ec2)

The AWS deployment is created for testing and destroyed afterwards to avoid cost, so the always-on demo is the Render link above.

## Running on Kubernetes (local)

The app also runs on a local [kind](https://kind.sigs.k8s.io/) cluster using the manifests in `k8s/`: a Deployment with 2 replicas, a Service, readiness and liveness probes, resource requests and limits, and a Postgres Deployment. Credentials live in a Kubernetes Secret created at deploy time and are never committed.

```bash
kind create cluster --name sre-lab
docker build -t incident-tracker:local .
kind load docker-image incident-tracker:local --name sre-lab

PASS=$(openssl rand -hex 12)
kubectl create secret generic app-secrets \
  --from-literal=POSTGRES_PASSWORD="$PASS" \
  --from-literal=API_KEY="$(openssl rand -hex 16)" \
  --from-literal=DATABASE_URL="postgresql://incident:${PASS}@postgres:5432/incidents"

kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/app.yaml
kubectl exec deploy/incident-tracker -- python create_tables.py
kubectl port-forward svc/incident-tracker 8080:80
```

![Pods, deployments and services](docs/k8s-resources.png)

![App running on the cluster](docs/k8s-app-running.png)

### What I tested

- **Scaling:** scaled the app from 2 to 4 replicas and back with `kubectl scale`.
- **Self-healing:** deleted the app pods and watched the Deployment recreate them.
- **Failed rollout and rollback:** rolled out a non-existent image. The new pod failed to start while the existing pods kept serving, and `kubectl rollout undo` restored the working version.
- **Dependency failure:** scaled Postgres to zero. The app pods stayed Ready and `/` still returned 200, but requests that needed the database failed.
- **Debugging:** used `kubectl get`, `describe`, `logs`, and `get events` to find causes.

### Notes

- The readiness probe only calls `/`, so a pod can report Ready while its database is down (I reproduced this by scaling Postgres to zero). A production setup would use a health endpoint that checks the database connection.
- In my environment the kind node could not resolve DNS, so the `postgres:16` image had to be loaded from the host instead of pulled by the cluster.
- This is a local learning setup, not a production cluster.

## What I'd add next

- Real health checks (HTTP ping / server agent) instead of simulated data
- Prometheus and Grafana monitoring
- Automated tests (pytest) in the CI pipeline before the build step