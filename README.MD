# Cloud-Native Employee Document Portal (Evolutionary Project)

## Project Overview
This project is a simulation of a real-world **Enterprise Document Management System**. The goal is to build a scalable, secure web application where employees can register their details and securely upload documents (Resumes/IDs).

**The twist:** This is an **Evolutionary DevOps Project**. Instead of building the complex infrastructure immediately, I am building it in strict phases to demonstrate mastery over the entire Software Development Life Cycle (SDLC):

---
### ⚠️ This project is intentionally built in phases. Each phase is available as a separate Git branch to showcase real-world system evolution.
---

1.  Local Development
2.  **Containerization (Docker) (Current Phase)**
3.  Orchestration (Kubernetes)
4.  Cloud Integration (AWS S3 & RDS)
5.  Automation (CI/CD Pipelines)

---
## 🐳 Phase 2: Containerization with Docker & Docker Compose

In Phase 2, the application was containerized to ensure **environment** **consistency**, reproducible deployments, and to prepare the system for cloud-native execution.

The goal of this phase was not scaling, but validating that the application behaves identically inside a container while handling data persistence correctly.

### What Changed in Phase 2

- Flask application containerized using a multi-stage Dockerfile
- Build and runtime layers separated to reduce final image size
- Docker Compose introduced for local orchestration
- Persistent storage implemented using bind-mounted volumes
- Application exposed using explicit port mapping (5000:5000)
- Local filesystem replaced by container-mounted paths

### Tech Stack (Phase 2)
- `Docker` (multi-stage builds)
- `Docker Compose`
- `python:3.12-slim` (builder stage)
- `python:3.12-alpine` (runtime stage)
### Architecture Summary (Phase 2)

- Flask application runs inside a Docker container
- SQLite database is mounted from the host into the container
- Uploaded files are mounted from the host into the container
- Containers remain ephemeral, data remains persistent
- Container restarts do not result in data loss
- This phase highlights the difference between application lifecycle and data lifecycle.

### Run Using Docker Compose
``` bash 
docker compose up -d
```

### The application will be available at:

``` bash 
http://localhost:5000
```

## Phase 2 Observations & Learnings

#### 1. Containers cannot be treated as permanent storage
- **`Meaning:`** Containers are disposable. They can be stopped, removed, or recreated at any time without warning.
- **`Lesson:`** Application code runs inside containers, but data must live outside containers using volumes or external storage.

#### 2. Bind-mounted volumes lock directories while containers are running
- **`Meaning:`** When Docker bind-mounts a host directory into a container, the Linux kernel marks that directory as `in use`.
- **`Lesson:`** While a container is running, mounted directories should not be modified or deleted from the host.

#### 3. Attempting to delete mounted paths results in `resource busy` errors
- **`Meaning:`** The Linux kernel prevents deletion of active mount points to avoid filesystem corruption.
- **`Lesson:`** A resource busy error is a signal that volumes are correctly attached, not a failure.
#### 4. Container filesystem ownership differs from host filesystem
- **`Meaning:`** Files created inside containers are typically owned by root, even when mounted on the host.
- **`Lesson:`** File ownership and permissions must be planned explicitly in production systems (**Docker**, **Kubernetes**).
This behavior is expected during local development.



📂 `Project Structure` (Phase 2)
``` text
employee-portal/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── templates/
│   └── index.html
├── Data/
│   ├── instance/        # SQLite DB (bind-mounted from host)
│   └── uploads/         # Uploaded files (bind-mounted from host)
```