# Git Branching Strategy

## Branching Model

LoanTrack uses a simple feature-branch workflow with `main` as the stable release branch and `develop` as the integration branch.

```text
main
  |
  +-----------------------------+
                                |
                           develop
                                |
              +-----------------+------------------+
              |                 |                  |
       feature/application   feature/docker   feature/kubernetes
              |                 |                  |
              +-------- Pull Requests ------------+
                                |
                                v
                             develop
                                |
                                v
                              main
```

### Branches

- `main` — stable, deployable release branch.
- `develop` — integration branch where completed feature work is combined.
- `feature/*` — short-lived branches for individual parts of the assignment.

Each feature branch is created from `develop` and merged back into `develop` using a Pull Request.

Examples used in this project:

```text
feature/application-foundation
feature/dockerization
feature/kubernetes-workloads
feature/documentation
```

## Pull Request Rules

- No direct feature commits are made to `main` or `develop`.
- Every feature branch is merged through a Pull Request.
- Pull Requests have a meaningful description.
- At least one review comment is added to the author's own diff as part of the required self-review.
- Feature branches are not squashed or tidied after merging so the development history remains visible.
- `main` is kept deployable.

## Development Flow

For a new part of the project:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<short-name>
```

After completing and testing the work:

```bash
git status
git diff --check
git add <files>
git commit -m "feat: describe the change"
git push -u origin feature/<short-name>
```

A Pull Request is then opened from:

```text
feature/<short-name> → develop
```

After the Pull Request is reviewed and merged, the local `develop` branch is updated:

```bash
git checkout develop
git pull origin develop
```

## Why This Model Was Used

This model is simple enough for a small assignment but still separates stable code from work in progress.

Using separate feature branches also makes it easier to identify which part of the project introduced a change. Pull Requests provide a checkpoint for reviewing the work before it becomes part of the integration branch.