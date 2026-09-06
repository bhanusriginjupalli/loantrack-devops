# AI Usage

AI tools were used selectively as development and review aids, mainly for documentation, troubleshooting, alternative approaches, and checking infrastructure configuration. The application design, implementation, testing, debugging, and final decisions were reviewed and validated manually.

The goal was to use AI as an engineering assistant rather than rely on generated output without verification.

## AI Usage Summary

| Task | Tool | Accepted as-is? | What I did / Why |
|---|---|---|---|
| Initial architecture discussion | Claude | No | Used suggestions to compare deployment approaches, then selected a simple 3-tier architecture with Nginx, FastAPI, and PostgreSQL because it was easier to operate and explain. |
| Repository and Git workflow | ChatGPT | Partly | Used AI to check that the branching workflow matched the assignment. I created and maintained the actual branches, commits, merges, and Pull Requests. |
| FastAPI troubleshooting | Claude | No | AI helped narrow down the cause of the `/api/loans` HTTP 500 error. I inspected the application behaviour and fixed the missing FastAPI lifespan registration. |
| Docker configuration review | ChatGPT | Partly | Used AI to review Dockerfile structure, image size, environment-variable handling, non-root execution, and Compose wiring. I built the images and verified the results locally. |
| Docker Compose debugging | ChatGPT | No | Used AI suggestions while diagnosing service-health and frontend/backend routing issues. The final configuration was tested using Docker Compose and direct container/database checks. |
| Kubernetes manifest review | ChatGPT | Partly | Used AI to review Deployments, StatefulSet, Services, ConfigMap, Secret references, resources, and probes. I applied the manifests and verified them with kubectl. |
| Kubernetes database initialization | ChatGPT | No | AI helped identify that the Kubernetes PostgreSQL workload did not initially receive the migration/seed SQL. I added the init ConfigMap and recreated the database workload/PVC as required. |
| Health/readiness routing | ChatGPT | No | AI helped identify the Nginx fallback problem affecting `/readyz`. I changed the Nginx configuration to explicitly proxy the endpoint to the backend. |
| Reliability testing | Claude | Partly | Used AI to suggest practical checks for retry/backoff, scaling, rolling updates, pod recovery, and PostgreSQL persistence. I ran the commands and captured the actual results. |
| Documentation | ChatGPT | Partly | AI helped structure the README, branching strategy, issue log, and evidence sections. I reviewed the content and kept the commands and results tied to the actual project. |

## How AI Was Used

AI was mainly useful for:

- Reviewing infrastructure configuration and spotting missing or inconsistent wiring.
- Suggesting debugging paths when a container or Kubernetes workload behaved unexpectedly.
- Comparing implementation options and their operational trade-offs.
- Structuring technical documentation.
- Checking whether the implementation addressed the assignment requirements.

The final implementation was not accepted solely because an AI tool suggested it. Changes were built, run, and verified locally before being kept.

## Examples Where AI Was Wrong or Misleading

### 1. FastAPI startup behaviour

An initial implementation contained a lifespan function, but it was not registered with the FastAPI application. The application therefore started without initializing the database pool correctly. The important part of the debugging process was checking the actual runtime behaviour rather than assuming that defining the function was sufficient.

### 2. Kubernetes PostgreSQL initialization

The first Kubernetes PostgreSQL workload did not reproduce the initialization behaviour that already worked in Docker Compose. The database pod could start successfully while the application schema was still missing. This reinforced the need to verify database state directly instead of treating a healthy pod as proof that the application database was ready.

### 3. Frontend readiness endpoint

The frontend's generic Nginx SPA fallback initially intercepted `/readyz`. AI suggestions helped identify the routing issue, but the fix was validated by making the actual request and checking that the response came from the backend.

## Verification Approach

For infrastructure-related suggestions, I preferred observable checks over assumptions. Examples include:

```text
docker compose ps
docker images
docker exec <container> whoami
curl /healthz
curl /readyz
psql queries against PostgreSQL
kubectl get all -n loantrack
kubectl get pvc,configmap,secret -n loantrack
kubectl rollout status
kubectl rollout undo
kubectl delete pod
```