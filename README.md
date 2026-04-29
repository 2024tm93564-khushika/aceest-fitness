# 🏋️ ACEest Fitness & Gym — CI/CD Pipeline

**SEZG514 Introduction to DevOps | Individual Assignment 2**
**Student:** Khushika Ranjan | **BITS ID:** 2024TM93564

---

## 📋 Project Overview

ACEest Fitness & Gym is a Flask REST API backed by SQLite, representing a fitness and gym management system. This repository demonstrates a fully automated, test-driven CI/CD pipeline built with industry-standard open-source DevOps tools.

The pipeline is orchestrated by **Jenkins**, polls the GitHub repository every minute, enforces quality via **SonarQube**, containerises the app via **Docker**, and deploys to a local **Kubernetes (Minikube)** cluster with zero downtime.

---

## 🗂️ Repository Structure

```
aceest-fitness/
├── ACEest_Fitness.py          # Main Flask application (v3.2.4)
├── test_app.py                # Pytest test suite (19 test cases)
├── Dockerfile                 # Docker image build instructions
├── Jenkinsfile                # Declarative CI/CD pipeline definition
├── docker-compose.yml         # Local multi-container setup
├── requirements.txt           # Python dependencies
├── k8s/                       # Kubernetes YAML manifests
│   ├── deployment.yaml
│   └── service.yaml
└── versions/                  # Historical application versions (v1.0 → v3.2.4)
```

---

## 🛠️ CI/CD Toolchain

| Layer | Tool | Role |
|---|---|---|
| Version Control | Git + GitHub | Feature-branch workflow; Pull Requests to `main`; structured commit tagging |
| CI/CD Server | Jenkins (LTS) | SCM polling every minute (`* * * * *`); multi-stage declarative Jenkinsfile |
| Testing | Pytest | 19-test suite — endpoints, RBAC auth, domain logic; mandatory pre-build gate |
| Code Quality | SonarQube | Static analysis; security hotspots; quality gate (bugs, coverage, complexity) |
| Containerisation | Docker | `python:3.10-slim` base; semantic version tags; pushed to Docker Hub registry |
| Orchestration | Kubernetes / Minikube | Rolling Update deployment; readiness-probe-gated traffic switch; zero downtime |

---

## ⚙️ Pipeline Flow

```
SCM Poll & Checkout  →  Pytest Suite  →  SonarQube Gate  →  Docker Build & Push  →  K8s Rolling Deploy  →  Live Cluster (v3.2.4)
```

Each stage acts as a mandatory quality gate — any failure aborts the pipeline run and prevents defective code from reaching the registry or cluster.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Hub account
- Jenkins (LTS)
- Minikube + kubectl
- SonarQube (local or hosted)

### 1. Clone the Repository

```bash
git clone https://github.com/2024tm93564-khushika/aceest-fitness.git
cd aceest-fitness
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application Locally

```bash
python ACEest_Fitness.py
```

The API will be available at `http://127.0.0.1:5000`.

### 4. Run Tests

```bash
python -m pytest
```

Expected: **19 tests passed**.

### 5. Build & Run with Docker

```bash
# Build the image
docker build -t 2024tm93564/aceest-fitness:v3.2.4 .

# Run the container
docker run -p 5000:5000 2024tm93564/aceest-fitness:v3.2.4
```

### 6. Run with Docker Compose

```bash
docker-compose up
```

---

## ☸️ Kubernetes Deployment

### Apply Manifests

```bash
# Start Minikube
minikube start

# Apply deployment and service
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check rollout status
kubectl get pods
kubectl rollout status deployment/aceest-fitness
```

### Access the Live Endpoint

```bash
# Port-forward to access locally
kubectl port-forward svc/aceest-fitness 8080:80
```

Expected response:

```json
{
  "message": "ACEest API v3.2.4 is running",
  "status": "healthy",
  "version": "3.2.4"
}
```

### Rolling Update (Zero Downtime)

```bash
kubectl set image deployment/aceest-fitness aceest-fitness=2024tm93564/aceest-fitness:<new-tag>
kubectl rollout status deployment/aceest-fitness
```

### Rollback

```bash
kubectl rollout undo deployment/aceest-fitness
```

---

## 🔁 Jenkins Pipeline

The `Jenkinsfile` defines the following stages:

1. **Checkout Code** — Clones the repository from GitHub
2. **Unit Tests** — Installs dependencies and runs the full Pytest suite
3. **SonarQube Quality Gate** — Runs static analysis; blocks build on failure
4. **Build & Push Docker Image** — Builds the Docker image and pushes to Docker Hub
5. **Prepare for Kubernetes Deployment** — Triggers rolling update on the cluster

To configure Jenkins:
- Add Docker Hub credentials with ID `docker-hub-creds`
- Point the pipeline to this repository's `Jenkinsfile`
- Enable SCM polling (`* * * * *`) or GitHub webhook triggers

---

## 📊 Key Automation Outcomes

| Dimension | Before CI/CD | After CI/CD Pipeline |
|---|---|---|
| Deployment method | Manual script execution | Fully automated on every PR merge to `main` |
| Test execution | Manual / optional | Mandatory gate; 19 Pytest cases on every build |
| Artefact versioning | None | 10 immutable Docker Hub tags (v1.0 – v3.2.4) |
| Deployment safety | Full service outage during updates | Zero downtime via Rolling Update (`maxUnavailable: 0`) |
| Mean time to deploy | 15–30 min (manual) | < 7 min (fully automated) |
| Rollback capability | Manual redeployment | Instant via `kubectl rollout undo` |
| Fault detection | Post-deployment user reports | Pre-deployment CI gate failure |

---

## 🐳 Docker Hub

All versioned images are published at:
**[hub.docker.com/r/2024tm93564/aceest-fitness](https://hub.docker.com/r/2024tm93564/aceest-fitness)**

```bash
# Pull the latest image
docker pull 2024tm93564/aceest-fitness:v3.2.4
```

---

## 📝 Course Details

| | |
|---|---|
| **Course** | SEZG514 — Introduction to DevOps |
| **Semester** | 2025–26, Second Semester |
| **Assignment** | Individual Assignment 2 — CI/CD Pipeline Implementation |
| **Submitted To** | Prof. A Abdul Rahman |
| **Student** | Khushika Ranjan |
| **BITS ID** | 2024TM93564 |
| **Institution** | BITS Pilani, Pilani Campus |