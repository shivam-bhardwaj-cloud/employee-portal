# Cloud-Native Employee Document Portal (Evolutionary Project)

## Project Overview
This project is a simulation of a real-world **Enterprise Document Management System**. The goal is to build a scalable, secure web application where employees can register their details and securely upload documents (Resumes/IDs).

**The twist:** This is an **Evolutionary DevOps Project**. Instead of building the complex infrastructure immediately, I am building it in strict phases to demonstrate mastery over the entire Software Development Life Cycle (SDLC):

---
### ⚠️ This project is intentionally built in phases. Each phase is available as a separate Git branch to showcase real-world system evolution.
---

1.  Local Development
2.  Containerization (Docker)
3.  **Orchestration (Kubernetes) (Current Phase)**
4.  Cloud Integration (AWS S3 & RDS)
5.  Automation (CI/CD Pipelines)

---
## Phase 3: Kubernetes Deployment with Persistent Storage (KIND)

In Phase 3, the containerized application was deployed to a Kubernetes cluster to move beyond single-node execution and understand real orchestration behavior.

The goal of this phase was not **high availability** or **production scaling**, but to validate **pod lifecycle, replicas, and persistent storage behavior** inside Kubernetes.

### What Changed in Phase 3

- Application deployed on Kubernetes using Deployment
- Multiple replicas managed by Kubernetes
- Dedicated Namespace created for isolation
- Application exposed internally using Service
- Persistent storage implemented using PersistentVolumeClaims (PVCs)
---
- Separate volumes created for:
- Uploaded files
- SQLite database
---
- Data persistence validated across pod deletion and recreation
- Local Kubernetes cluster created using **KIND**

### Tech Stack (Phase 3)
- `Kubernetes`
- `KIND` (Kubernetes IN Docker)
- `kubectl`
- `PersistentVolumeClaim`
- `local-path-storage` (default KIND storage class)
- Docker image from Phase 2

### Architecture Summary (Phase 3)
- Flask application runs inside Kubernetes pods
- Pods are managed by a Deployment with **3 replicas**
- A Service routes traffic to pods
- Uploaded files are stored in `/app/uploads` via PVC
- SQLite database is stored in `/app/instance` via PVC
- Pods remain **ephemeral**
- Data remains **persistent**
- Pod restarts and deletions do not cause data loss
- This phase highlights the separation between **pod lifecycle** and **data- lifecycle**

### Run on Kubernetes (KIND)
``` bash 
kubectl apply -f namespace.yml
kubectl apply -f pvc.yml
kubectl apply -f db-pvc.yml
kubectl apply -f deployment.yml
kubectl apply -f service.yml
```

### Access the Application

``` bash 
kubectl port-forward svc/employee-portal-svc -n employee-portal-ns 5000:80

```
### Application available at:
``` bash
http://localhost:5000
```

## Phase 3 Observations & Learnings

#### 1.Pods are ephemeral, volumes are not
- **`Meaning:`** Kubernetes freely destroys and recreates pods.
- **`Lesson:`** Any important data must live inside Persistent Volumes, not inside pods.

#### 2.PVCs persist data across pod restarts
- **`Meaning:`** Deleting a pod does not delete its attached volume.
- **`Lesson:`** PersistentVolumeClaims decouple storage from pod lifecycle.

#### 3. Multiple replicas share the same volume (ReadWriteOnce)
- **`Meaning:`** SQLite works here only because KIND schedules pods carefully.
- **`Lesson:`** SQLite is acceptable for learning, not for real multi-replica production systems.

#### 4. Kubernetes does not expose containers directly
- **`Meaning:`** You cannot use `docker exec` to inspect application containers.
- **`Lesson:`** Always interact with workloads using kubectl exec.

#### 5. Services expose pods, not containers
- **`Meaning:`** Port-forwarding targets Services or Pods, not Docker containers.
- **`Lesson:`** Networking is abstracted at the Kubernetes layer.

## Problems Faced & Troubleshooting

**Issue 1:** `/app` directory not visible using Docker commands.
- **`Cause:`** Kubernetes pods run inside node containers managed by KIND.
- **`Fix:`** 
``` bash
kubectl exec -it <pod-name> -n <ns-name> -- sh
```
---
**Issue 2:** `permission denied` **when binding to port 80**
- **`Cause:`** Ports below 1024 require root privileges.
- **`Fix:`** Use high ports like `5000` during port-forwarding.
---

**Issue 3:** Data disappeared after pod deletion (initially)
- **`Cause:`** Volumes were not mounted correctly in Deployment.
- **`Fix:`** Explicitly mount PVCs to `/app/uploads` and `/app/instance`.

---

**Issue 4:** SQLite database location confusion
- **`Cause:`** Flask auto-creates databases inside the instance/ directory.
- **`Fix:`** Persist /app/instance using a dedicated PVC.

---

📂 `Project Structure` (Phase 3)
``` text

employee-portal/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── templates/
│   └── index.html
├── k8s (KIND)/
│   ├── cluster.yml
│   ├── namespace.yml
│   ├── deployment.yml
│   ├── service.yml
│   ├── pvc.yml
│   └── db-pvc.yml

```