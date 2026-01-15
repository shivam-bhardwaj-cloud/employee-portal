# Cloud-Native Employee Document Portal (Evolutionary Project)

## Project Overview
This project is a simulation of a real-world **Enterprise Document Management System**. The goal is to build a scalable, secure web application where employees can register their details and securely upload documents (Resumes/IDs).

**The twist:** This is an **Evolutionary DevOps Project**. Instead of building the complex infrastructure immediately, I am building it in strict phases to demonstrate mastery over the entire Software Development Life Cycle (SDLC):

---
### ⚠️ This project is intentionally built in phases. Each phase is available as a separate Git branch to showcase real-world system evolution.
---

1.  Local Development
2.  Containerization (Docker)
3.  Orchestration (Kubernetes)
4.  **Cloud Integration (AWS S3 & RDS) (Current Phase)**
5.  Automation (CI/CD Pipelines)

---
## Phase 4: Cloud Integration using AWS S3 + AWS RDS

IIn Phase 4, the application moves from local storage and local databases to fully cloud-managed storage & database infrastructure. This transition enables true stateless application behavior, durable storage, and secure credential management.

The goal of this phase is not only to `push things to the cloud` but to validate real production concerns such as:

- Data durability
- Horizontal scalability
- Stateless containers
- Secure authentication without static keys
- Eliminating local single-node bottlenecks

### What Changed in Phase 4

- File uploads now go to **Amazon S3** instead of local disk.
- Employee metadata stored in **Amazon RDS** (PostgreSQL) - instead of SQLite.
- Python backend updated to use **SQLAlchemy ORM** with a - PostgreSQL driver.
- **IAM Instance Role** replaces AWS Access Keys for secure - authentication.
- Flask development server replaced with **Gunicorn** for - production readiness.
- Dockerfile switched from Alpine → Debian Slim for - psycopg2 support.
- All local volumes related to storage were removed.
- Application runs as a **Stateless Cloud-Ready Service**.

### Tech Stack (Phase 4)

- `Flask` (Backend Framework)
- `Gunicorn` (WSGI Production Server)
- `SQLAlchemy` + `psycopg2-binary` (ORM + PostgreSQL Driver)
- `Amazon S3` (Object Storage)
- `Amazon RDS (PostgreSQL)` (Managed Relational DB)
- `AWS IAM` (Instance Roles for Credential Management)
- `Docker` (Container Runtime)
- `TailwindCSS` (Frontend Styling)
- `boto3` (AWS SDK)

### Architecture Summary (Phase 4)

- Web traffic hits a Flask application running under **Gunicorn**.
- Application stores files in an **S3 bucket** instead of local folders.
- Application stores metadata in **AWS RDS PostgreSQL**.
- No persistent volumes are mounted on the container.
- Application becomes **stateless** and fault-tolerant.
- IAM Role provides **temporary secure credentials** to S3 (no keys in code).

This phase highlights the separation between:

- **Application compute layer**
- **Object storage layer**
- **Relational data layer**

### Run on Cloud (EC2 Example)

- Attach IAM Role with S3 permissions to instance
- Install Docker + Docker Compose
- Create `.env` file with RDS details
- Run the application

Run:
``` bash
docker compose up --build -d
```

---

### Application Access at:
``` bash
http://<public-ip>:5000
```

``` bash
http://localhost:5000
```

## Phase 4 Observations & Learnings

#### 1.Object Storage Replaces PVCs for File Uploads
- **`Meaning:`** Local disk storage does not scale across replicas.
- **`Lesson:`** S3 provides durability, scalability, and eliminates disk affinity.

#### 2.RDS Replaces SQLite for Multi-User & Durable Data
- **`Meaning:`** SQLite cannot handle concurrent cloud workloads.
- **`Lesson:`** Cloud DB engines solve scaling, backups, and failover.

#### 3. IAM Roles Replace Static Credentials
- **`Meaning:`** Hardcoded AWS keys are insecure and unmanageable.
- **`Lesson:`** IAM-based auth enables automatic credential rotation.

#### 4. Stateless Containers Improve Resilience
- **`Meaning:`** No local volumes means no data loss on container eviction.
- **`Lesson:`** Containers become disposable and safe to auto-scale.

#### 5. Flask Dev Server Is Not Production-Ready
- **`Meaning:`** Debug server lacks concurrency and security.
- **`Lesson:`** Debug server lacks concurrency and security.

## Problems Faced & Troubleshooting

**Issue 1:** `psycopg2` failing to install on Alpine
- **`Cause:`** Requires system libraries not available on Alpine by default
- **`Fix:`** Switched to `python:3.12-slim`

---
**Issue 2:** Credential handling confusion
- **`Cause:`** AWS SDK defaults require credentials to exist.
- **`Fix:`** UUsed IAM Role attached to EC2 for secure automatic auth.

---

**Issue 3:** SQLite locking under multi-request traffic
- **`Cause:`** SQLite uses file-level locking
- **`Fix:`** EMigrated DB layer to AWS RDS PostgreSQL

---

**Issue 4:** Local uploads not accessible after restart.
- **`Cause:`** No shared persistent filesystem
- **`Fix:`** Migrated to S3 object storage

---

📂 `Project Structure` (Phase 4)
``` text

employee-portal/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                # Local config (ignored in Git)
├── .dockerignore
├── .gitignore
├── k8s (KIND)/
└── templates/
    └── index.html

```
---

### Environment Variables
.env file should contain:

``` bash
SECRET_KEY=change_me
POSTGRES_HOST=<rds-endpoint>
POSTGRES_PORT=<postgres-port>
POSTGRES_USER=<postgres-username>
POSTGRES_PASSWORD=<postgres-password>
POSTGRES_DB=employee_portal

AWS_REGION=us-east-1
S3_BUCKET=<your-unique-bucket-name>
```

**Note:** AWS Access Keys are not required when running on EC2 with IAM Roles.

### AWS S3 Upload (Python)
``` python
s3_client.upload_fileobj(
    file,
    app.config['S3_BUCKET'],
    filename,
    ExtraArgs={'ContentType': file.content_type}
)
file_url = f"https://{app.config['S3_BUCKET']}.s3.{app.config['AWS_REGION']}.amazonaws.com/{filename}"
```
### RDS Metadata Insert
``` python
new_emp = Employee(name=name, email=email, role=role, resume_url=file_url)
db.session.add(new_emp)
db.session.commit()
```

---

## Troubleshooting / Verification

To verify direct connectivity to AWS RDS using `psql`, run:

``` bash 
PGPASSWORD=<postgres-password> psql -h <rds-endpoint> -U <postgres-username> -d employee_portal
```
