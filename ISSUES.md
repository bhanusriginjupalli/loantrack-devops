# Issues Encountered

This document records three real implementation issues encountered while building and testing LoanTrack. Each issue is documented using the symptom, diagnosis, root cause, and fix so that the debugging process is reproducible.

---

## Issue 1 — `/api/loans` Returned HTTP 500

### Symptom

The frontend loaded, but requests to the backend `/api/loans` endpoint returned HTTP 500 instead of the expected loan data.

### Diagnosis

The backend process itself was running, but the database connection pool was not being initialized before the routes tried to use it. The FastAPI application had a lifespan function for startup and shutdown, but it was not registered with the FastAPI application instance.

### Root Cause

The `FastAPI()` application was created without passing the defined `lifespan` handler. Therefore, the startup code that creates the PostgreSQL connection pool was never executed.

### Fix

The application was changed to register the lifespan handler:

```python
app = FastAPI(title="LoanTrack API", lifespan=lifespan)
```

After rebuilding the backend image and restarting the Compose stack, `/api/loans` returned the seeded loan records successfully.

### Lesson

Defining a startup/shutdown function is not enough; it must also be explicitly connected to the framework lifecycle.

---

## Issue 2 — Kubernetes PostgreSQL Started Without the `loans` Table

### Symptom

The PostgreSQL pod became available, but the backend could not work with the expected database schema because the `loans` table had not been created.

### Diagnosis

The PostgreSQL container was healthy and accepting connections, so the problem was not basic database connectivity. Inspection of the PostgreSQL initialization showed that the migration and seed SQL files were not being mounted into the Kubernetes PostgreSQL container.

### Root Cause

The Docker Compose setup used the SQL files as PostgreSQL initialization scripts, but the Kubernetes StatefulSet did not initially provide the same initialization files. As a result, PostgreSQL started with an empty application database.

### Fix

A Kubernetes ConfigMap named `loantrack-db-init` was added containing the versioned migration and seed SQL. It is mounted at:

```text
/docker-entrypoint-initdb.d/
```

The PostgreSQL StatefulSet was recreated with the initialization ConfigMap available. PostgreSQL then executed the migration and seed scripts, creating the `loans` table and inserting the five seed records.

The initialization was verified with PostgreSQL commands showing:

```text
CREATE TABLE
INSERT 0 5
```

and a subsequent query showing the five seeded loans.

### Lesson

Container initialization behaviour must be reproduced explicitly when moving from Docker Compose to Kubernetes. A working Compose volume/script configuration does not automatically exist in Kubernetes.

---

## Issue 3 — Frontend `/readyz` Returned HTML Instead of Backend Readiness

### Symptom

The Kubernetes frontend readiness endpoint did not return the backend's JSON readiness response. Instead, requesting `/readyz` returned the frontend application's HTML page.

### Diagnosis

The frontend is served by Nginx, while the readiness state belongs to the backend. Nginx's general frontend route used the SPA fallback:

```text
try_files $uri $uri/ /index.html;
```

Because `/readyz` did not have a dedicated Nginx location, the request was handled by the frontend fallback rather than being forwarded to the backend.

### Root Cause

There was no explicit Nginx routing rule for `/readyz`.

### Fix

A dedicated Nginx location was added:

```nginx
location = /readyz {
    proxy_pass http://backend:8000/readyz;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
}
```

After rebuilding the frontend image and restarting the stack, `/readyz` correctly returned the backend readiness response.

### Lesson

Infrastructure health endpoints need explicit routing when a reverse proxy sits in front of the application. Generic SPA fallback rules should not intercept operational endpoints.

---

## Summary

These issues were useful because they exposed problems at three different layers:

- **Application lifecycle:** FastAPI startup and connection-pool initialization.
- **Infrastructure initialization:** reproducing database initialization correctly in Kubernetes.
- **Reverse-proxy routing:** separating application routes from health/readiness endpoints.

The fixes were kept simple and configuration-focused, which matches the goal of making the deployment easy to understand and modify during a future operational/debugging round.
