# LoanTrack — DevOps/SRE Take-Home Assignment

LoanTrack is a small 3-tier loan tracking application deployed using Docker Compose and Kubernetes.

The application consists of a frontend, backend API, and PostgreSQL database. The main focus of this project is containerization, service communication, configuration and secret management, persistent storage, health checks, Kubernetes deployment, scaling, rollback, and basic self-healing.

## Architecture

```text
                         Browser
                            |
                            | HTTP
                            v
                 +----------------------+
                 |      Frontend        |
                 |   Nginx + HTML/JS    |
                 |      NodePort        |
                 +----------+-----------+
                            |
                            | /api/*
                            v
                 +----------------------+
                 |       Backend        |
                 | FastAPI + Uvicorn    |
                 |      ClusterIP       |
                 +----------+-----------+
                            |
                            | PostgreSQL
                            | Service DNS
                            v
                 +----------------------+
                 |     PostgreSQL       |
                 |     StatefulSet      |
                 |      ClusterIP       |
                 +----------+-----------+
                            |
                            v
                    Persistent PVC
```

The frontend does not connect directly to PostgreSQL. It communicates with the backend over HTTP, and only the backend has database credentials.

## Repository Structure

```text
loantrack-devops/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── index.html
│   │   └── app.js
│   ├── nginx.conf
│   ├── Dockerfile
│   └── .dockerignore
├── db/
│   ├── migrations/
│   │   └── 001_create_loans.sql
│   └── seed/
│       └── 001_seed_loans.sql
├── k8s/
│   ├── namespace.yaml
│   ├── config.yaml
│   ├── secret.example.yaml
│   ├── db-init-configmap.yaml
│   ├── postgres.yaml
│   ├── backend.yaml
│   └── frontend.yaml
├── scripts/
│   └── deploy.sh
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── BRANCHING.md
├── EVIDENCE.md
├── ISSUES.md
└── AI_USAGE.md
```

## Tools and Versions

The project was developed and tested with:

- Git
- Docker
- Docker Compose
- Minikube
- Kubernetes
- kubectl
- Python 3.12
- FastAPI
- PostgreSQL 17
- Nginx

The Kubernetes cluster used for testing was Minikube with the Docker driver.

## Application Endpoints

The backend exposes:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/loans` | List loans |
| POST | `/loans` | Add a loan |
| GET | `/healthz` | Process/liveness check |
| GET | `/readyz` | Database readiness check |
| GET | `/podinfo` | Returns backend pod name for scaling evidence |

The frontend also exposes `/healthz` and `/readyz` through Nginx for Kubernetes probes.

## Environment Variables

Local configuration is stored in a `.env` file which is intentionally ignored by Git.

Start from the example:

```bash
cp .env.example .env
```

The variables are:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DATABASE_HOST
DATABASE_PORT
BACKEND_PORT
FRONTEND_PORT
```

Never commit the real `.env` file.

## Docker Compose

### Start the application

From the repository root:

```bash
docker compose up -d --build
```

Check the containers:

```bash
docker compose ps
```

The expected services are:

```text
frontend
backend
postgres
```

Open:

```text
http://localhost:8080
```

The PostgreSQL database is initialized automatically with the migration and seed files.

### Verify the backend

```bash
curl http://localhost:8080/api/loans
```

Health:

```bash
curl http://localhost:8080/healthz
```

Readiness:

```bash
curl http://localhost:8080/readyz
```

### Stop the application

```bash
docker compose down
```

The PostgreSQL named volume is retained, so database data survives this command.

To remove the volume as well:

```bash
docker compose down -v
```

This deletes the PostgreSQL persistent volume, so existing database data is removed.

## Kubernetes

The Kubernetes resources are deployed into the dedicated:

```text
loantrack
```

namespace.

The architecture is:

```text
Frontend Deployment
       |
       | NodePort
       v
Frontend Service
       |
       | HTTP
       v
Backend ClusterIP Service
       |
       v
Backend Deployment
       |
       | PostgreSQL Service DNS
       v
PostgreSQL ClusterIP Service
       |
       v
PostgreSQL StatefulSet
       |
       v
PersistentVolumeClaim
```

### Start Minikube

```bash
minikube start --driver=docker
```

Check:

```bash
kubectl get nodes
```

### Create the Kubernetes Secret

The real database password is not stored in Git.

Create the Secret using:

```bash
kubectl create namespace loantrack

kubectl create secret generic loantrack-secret \
  -n loantrack \
  --from-literal=POSTGRES_PASSWORD=<your-password>
```

`k8s/secret.example.yaml` contains only a dummy example value.

### Deploy manually

Apply the resources in order:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/db-init-configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

Check the deployment:

```bash
kubectl get all -n loantrack
```

Check storage and configuration:

```bash
kubectl get pvc,configmap,secret -n loantrack
```

### Access the application

```bash
minikube service frontend -n loantrack --url
```

Keep the terminal open when using the Minikube URL with the Docker driver on Windows.

### Automated deployment

The repository contains:

```text
scripts/deploy.sh
```

It:

1. Checks Minikube.
2. Builds the backend image.
3. Builds the frontend image.
4. Loads both images into Minikube.
5. Applies the namespace and configuration.
6. Checks that the required Secret exists.
7. Deploys PostgreSQL.
8. Waits for PostgreSQL readiness.
9. Deploys the backend.
10. Waits for the backend rollout.
11. Deploys the frontend.
12. Waits for the frontend rollout.
13. Prints the application URL.

The script is POSIX shell compatible and can be run using Git Bash on Windows.

## Health Checks

### Backend

`/healthz` checks whether the backend process is alive and does not depend on the database.

`/readyz` checks database connectivity and returns an error status when the database cannot be reached.

Kubernetes uses:

- `/healthz` as the liveness probe
- `/readyz` as the readiness probe

### Frontend

Nginx provides:

- `/healthz`
- `/readyz`

These are used by Kubernetes for liveness and readiness.

### PostgreSQL

PostgreSQL uses `pg_isready` for its Kubernetes readiness and liveness probes.

## Reliability and Scaling

The backend uses a connection pool with retry and exponential backoff during startup.

A separate failure test was performed by starting the backend before PostgreSQL was available. The backend initially failed to resolve the database hostname and later received connection-refused errors while PostgreSQL was starting. It eventually connected successfully and became ready.

The backend was also scaled to three replicas:

```bash
kubectl scale deployment backend --replicas=3 -n loantrack
```

Requests sent through the backend ClusterIP Service were observed reaching all three backend pods.

A rolling update from:

```text
loantrack-backend:v1
```

to:

```text
loantrack-backend:v2
```

was completed successfully and then rolled back to `v1`.

Backend pod deletion was tested and Kubernetes recreated the missing replica.

PostgreSQL pod deletion was also tested. The StatefulSet recreated `postgres-0`, and the existing loan records remained because the database used a persistent PVC.

## Design Decisions

### Backend base image

A pinned Python slim image is used instead of `latest` to keep the image version predictable and reduce unnecessary image size.

### Frontend cache boundary

The frontend is a static Nginx application. Nginx also acts as the HTTP reverse proxy for `/api/`, so the browser does not need to know the backend service address.

### PostgreSQL: StatefulSet

PostgreSQL uses a StatefulSet because the database requires stable identity and persistent storage. A PVC is attached to the StatefulSet so data survives pod recreation.

### Liveness vs readiness

Liveness checks whether a process is functioning.

Readiness checks whether the application is able to serve requests correctly. For the backend, this includes checking database connectivity.

This prevents Kubernetes from sending normal application traffic to a backend that cannot currently access its database.

### Resource limits

CPU and memory requests provide Kubernetes scheduling information, while limits prevent a container from using unlimited resources.

### Kubernetes Secrets

Kubernetes Secret values are base64 encoded, not encrypted by default. Therefore, a Secret should not be treated as equivalent to encryption.

For a production system, I would use an external secret manager such as a cloud secret-management service or a dedicated secret-management system with appropriate access control and encryption.

## Security

- Real credentials are not committed.
- `.env` is ignored by Git.
- Kubernetes credentials are consumed using `secretKeyRef`.
- PostgreSQL is exposed only as a ClusterIP service.
- The frontend never connects directly to PostgreSQL.
- Docker containers run as non-root users where applicable.
- Docker build contexts exclude unnecessary files using `.dockerignore`.

## Evidence

Testing evidence and command outputs are documented in:

```text
EVIDENCE.md
```

This includes Docker, Compose, Kubernetes, scaling, rolling update, rollback, self-healing, persistence, and retry/recovery tests.

## Known Issues

Real development issues encountered during implementation are documented in:

```text
ISSUES.md
```

## AI Usage

AI assistance was used for parts of the implementation, debugging, documentation and reasoning. The actual commands, outputs and final project decisions were tested locally.

Details are documented in:

```text
AI_USAGE.md
```

## Git Workflow

The repository uses:

```text
main
  |
develop
  |
feature/*
```

Feature branches are created from `develop` and merged through pull requests.

`main` and `develop` are not used for direct feature development.

The branching approach and team-of-five recommendation are documented in:

```text
BRANCHING.md
```
