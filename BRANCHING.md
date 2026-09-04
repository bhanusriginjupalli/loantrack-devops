# Git Branching Strategy

## Branches

- `main` — stable and always deployable
- `develop` — integration branch for completed features
- `feature/*` — short-lived branches for individual parts of the assignment

## Workflow

Work is performed on a `feature/*` branch created from `develop`.

```text
feature/*
    │
    │ Pull Request
    ▼
develop
    │
    │ Pull Request
    ▼
main