# AI Life Automation Suite

A strictly isolated, production-grade monorepo containing three applications.

## Apps
1. **memory-journal-app**: Accepts image uploads, generates mock AI captioning, and stores metadata.
2. **doomscroll-breaker-app**: Tracks mock usage patterns, alerts on excessive use, and manages focus sessions.
3. **visual-intelligence-app**: A modular computer vision pipeline tracking mock detection events.

## Architecture
This monorepo adheres to a strict isolation policy. Apps share no runtime dependency and communicate, if at all, over network APIs. Every app provides its own Dockerfile and operates independently.

## Local Development & Testing
Each app has a dedicated test script (`scripts/test_<app>.sh`) which uses a temporary virtual environment to prevent system pollution.

To run all tests:
```bash
make test-all
```

To run all linting:
```bash
make lint-all
```

To clean temporary environments:
```bash
make clean
```

## Docker Execution (Docker-First)
All applications can run together via Docker Compose:

```bash
docker compose -f docker/docker-compose.yml up
```

To run individual apps:
```bash
docker compose -f docker/docker-compose.yml run memory-journal-app
docker compose -f docker/docker-compose.yml run doomscroll-breaker-app
docker compose -f docker/docker-compose.yml run visual-intelligence-app
```

To run tests within Docker:
```bash
docker compose -f docker/docker-compose.yml run memory-journal-app pytest
```

## CI/CD
GitHub Actions workflow verifies all apps by running Pytest and Coverage. Upon success, it packages each app as a ZIP artifact for deployment.
